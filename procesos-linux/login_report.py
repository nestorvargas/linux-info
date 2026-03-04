#!/usr/bin/env python3
"""Genera un reporte PDF con el número de inicios de sesión por usuario usando la salida de `last`.

Uso básico:
    python3 login_report.py --output login_report.pdf

Requisitos: reportlab (ver requirements.txt)
"""
import argparse
import subprocess
import re
from collections import defaultdict, deque
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


def collect_last_lines():
    """Ejecuta `last` y devuelve una lista de líneas relevantes (hasta 'wtmp begins')."""
    try:
        res = subprocess.run(["last", "-w"], capture_output=True, text=True, check=True)
        out = res.stdout.splitlines()
    except Exception:
        # fallback simple: intentar leer /var/log/wtmp no es trivial; devolver vacío
        return []

    lines = []
    for line in out:
        if line.strip().startswith("wtmp begins"):
            break
        if not line.strip():
            continue
        # ignorar entradas de reboot/shutdown/boot para conteo de usuarios
        if line.startswith(("reboot", "shutdown", "wtmp", "boot")):
            continue
        lines.append(line.rstrip())
    return lines


def parse_duration_from_last(line):
    """Extrae la duración entre paréntesis al final de una línea de `last`.

    Retorna duración en segundos o None si no se encuentra/está "still logged in".
    """
    # buscar patrones como (00:10), (1+02:03), (00:10:05)
    m = re.search(r"\((?P<days>\d+\+)?(?P<h>\d+):(?P<m>\d+)(?::(?P<s>\d+))?\)\s*$", line)
    if not m:
        return None
    days = m.group('days')
    days_val = int(days[:-1]) if days else 0
    h = int(m.group('h') or 0)
    mm = int(m.group('m') or 0)
    s = int(m.group('s') or 0)
    return days_val * 86400 + h * 3600 + mm * 60 + s


def analyze(lines, recent_per_user=5):
    counts = defaultdict(int)
    recent = defaultdict(lambda: deque(maxlen=recent_per_user))
    total_seconds = defaultdict(int)
    sessions = defaultdict(list)  # lista de (line, seconds_or_None)

    for line in lines:
        parts = line.split()
        if not parts:
            continue
        user = parts[0]
        if user in ("reboot", "shutdown", "wtmp", "boot"):
            continue
        counts[user] += 1
        recent[user].appendleft(line)

        secs = parse_duration_from_last(line)
        if secs:
            total_seconds[user] += secs
        sessions[user].append((line, secs))

    return counts, recent, total_seconds, sessions


def seconds_to_hms(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def build_pdf(output_path, counts, recent, total_seconds, sessions):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elems = []

    elems.append(Paragraph("Reporte de inicios de sesión por usuario", styles["Title"]))
    elems.append(Paragraph(f"Generado: {datetime.now().isoformat(sep=' ', timespec='seconds')}", styles["Normal"]))
    elems.append(Spacer(1, 12))

    # Tabla resumen
    data = [["Usuario", "Veces", "Tiempo total"]]
    for user, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        total = seconds_to_hms(total_seconds.get(user, 0)) if total_seconds.get(user) else "-"
        data.append([user, str(cnt), total])

    t = Table(data, colWidths=[200, 100])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))
    elems.append(t)
    elems.append(Spacer(1, 12))

    # Detalle recientes
    elems.append(Paragraph("Entradas recientes (por usuario)", styles["Heading2"]))
    for user, lines in sorted(recent.items(), key=lambda x: -len(x[1])):
        elems.append(Paragraph(f"Usuario: {user} — {len(lines)} últimas entradas", styles["Heading3"]))
        for l in lines:
            elems.append(Paragraph(l, styles["Code"]))
        elems.append(Spacer(1, 6))

    elems.append(Paragraph("Detalle de sesiones (duración si está disponible)", styles["Heading2"]))
    for user, sess_list in sorted(sessions.items(), key=lambda x: -len(x[1])):
        elems.append(Paragraph(f"Usuario: {user}", styles["Heading3"]))
        subdata = [["Línea", "Duración"]]
        for line, secs in sess_list:
            dur = seconds_to_hms(secs) if secs else ("still" if "still" in line.lower() or "logged in" in line.lower() else "-")
            # limitar longitud de línea para la tabla
            display_line = line if len(line) < 120 else line[:117] + "..."
            subdata.append([display_line, dur])
        st = Table(subdata, colWidths=[380, 100])
        st.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ]))
        elems.append(st)
        elems.append(Spacer(1, 8))

    doc.build(elems)


def main():
    parser = argparse.ArgumentParser(description="Genera un PDF con conteo de logins por usuario (usa `last`)")
    parser.add_argument("--output", "-o", default="login_report.pdf", help="Archivo PDF de salida")
    args = parser.parse_args()

    lines = collect_last_lines()
    counts, recent = analyze(lines)
    build_pdf(args.output, counts, recent)
    print(f"Reporte generado: {args.output}")


if __name__ == "__main__":
    main()
