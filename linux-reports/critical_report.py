#!/usr/bin/env python3
"""Genera un reporte de fallos críticos del servidor y lo envía por correo.

Recolecta información de:
- `systemctl --failed`
- `journalctl -p err -b` (errores desde el último arranque)
- `dmesg` (niveles err/crit/alert/emerg)
- archivos comunes de logs (`/var/log/syslog`, `/var/log/messages`, `/var/log/auth.log`)

Envía correo usando sendmail local si está disponible, o SMTP si se indican parámetros.

Ejemplo:
  python3 critical_report.py --to admin@example.com --subject "Reporte fallos críticos" --attach-pdf

"""
import argparse
import os
import shlex
import subprocess
import sys
from datetime import datetime
from email.message import EmailMessage
import smtplib
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


def run_cmd(cmd, timeout=15):
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return res.stdout.strip()
    except Exception as e:
        return f"ERROR running {' '.join(shlex.quote(c) for c in cmd)}: {e}"


def collect_systemctl_failed():
    return run_cmd(["systemctl", "--failed", "--no-pager", "--no-legend"]) or "(no failed units)"


def collect_journal(lines=500):
    return run_cmd(["journalctl", "-p", "err", "-b", "-n", str(lines), "--no-pager"]) or "(no journal errors found)"


def collect_dmesg():
    # dmesg may require root to show all messages
    return run_cmd(["dmesg", "-T", "-l", "err,crit,alert,emerg"]) or "(no kernel critical messages)"


COMMON_LOGS = ["/var/log/syslog", "/var/log/messages", "/var/log/auth.log", "/var/log/kern.log"]


def collect_log_files(lines=200):
    found = {}
    for p in COMMON_LOGS:
        if os.path.exists(p):
            try:
                out = run_cmd(["tail", "-n", str(lines), p])
            except Exception:
                out = f"(cannot read {p})"
            found[p] = out
    if not found:
        found["(none)"] = "No common log files found or accessible"
    return found


def build_report():
    ts = datetime.now().isoformat(sep=' ', timespec='seconds')
    parts = []
    parts.append(f"Reporte de fallos críticos\nGenerado: {ts}\nHost: {os.uname().nodename}\n")

    parts.append("== systemctl --failed ==\n")
    parts.append(collect_systemctl_failed())

    parts.append("\n== journalctl (errores desde arranque) ==\n")
    parts.append(collect_journal())

    parts.append("\n== dmesg (err/crit/alert/emerg) ==\n")
    parts.append(collect_dmesg())

    parts.append("\n== Archivos de logs (últimas líneas) ==\n")
    logs = collect_log_files()
    for path, content in logs.items():
        parts.append(f"-- {path} --\n")
        parts.append(content)

    return "\n".join(parts)


def generate_pdf(text, out_pdf):
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("reportlab no está disponible; instale reportlab si desea PDF")
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(out_pdf, pagesize=A4)
    elems = []
    elems.append(Paragraph("Reporte de fallos críticos", styles['Title']))
    elems.append(Paragraph(f"Generado: {datetime.now().isoformat(sep=' ', timespec='seconds')}", styles['Normal']))
    elems.append(Spacer(1, 12))

    # dividir texto por secciones grandes
    for block in text.split('\n\n'):
        # limitar tamaño de párrafo
        elems.append(Paragraph(block.replace('\n', '<br/>'), styles['Code']))
        elems.append(Spacer(1, 6))

    doc.build(elems)


def send_via_sendmail(msg: EmailMessage):
    sendmail = shutil.which('sendmail') or shutil.which('/usr/sbin/sendmail')
    if not sendmail:
        return False, 'sendmail not found'
    p = subprocess.Popen([sendmail, '-oi', '-t'], stdin=subprocess.PIPE)
    p.communicate(msg.as_bytes())
    return p.returncode == 0, f'sendmail exit {p.returncode}'


def send_email(msg: EmailMessage, smtp_server=None, smtp_port=0, smtp_user=None, smtp_pass=None):
    # Try local sendmail first
    try:
        import shutil
        sendmail = shutil.which('sendmail') or shutil.which('/usr/sbin/sendmail')
    except Exception:
        sendmail = None

    if sendmail:
        p = subprocess.Popen([sendmail, '-oi', '-t'], stdin=subprocess.PIPE)
        p.communicate(msg.as_bytes())
        return p.returncode == 0, f'sendmail exit {p.returncode}'

    if not smtp_server:
        return False, 'No sendmail and no SMTP server provided'

    try:
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=20)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port or 25, timeout=20)
            if smtp_port == 587:
                server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)
        server.quit()
        return True, 'sent via SMTP'
    except Exception as e:
        return False, str(e)


def make_email(subject, sender, recipients, body_text, attach_path=None, attach_pdf=None):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    msg.set_content(body_text)

    if attach_path and os.path.exists(attach_path):
        with open(attach_path, 'rb') as f:
            data = f.read()
        msg.add_attachment(data, maintype='text', subtype='plain', filename=os.path.basename(attach_path))

    if attach_pdf and os.path.exists(attach_pdf):
        with open(attach_pdf, 'rb') as f:
            data = f.read()
        msg.add_attachment(data, maintype='application', subtype='pdf', filename=os.path.basename(attach_pdf))

    return msg


def main():
    parser = argparse.ArgumentParser(description='Genera y envía un reporte de fallos críticos')
    parser.add_argument('--to', required=True, help='Destinatarios (coma-separados)')
    parser.add_argument('--from', dest='sender', default=f'root@{os.uname().nodename}', help='Dirección remitente')
    parser.add_argument('--subject', default='Reporte fallos críticos', help='Asunto del correo')
    parser.add_argument('--output', default='/tmp/critical_report.txt', help='Archivo de texto de salida')
    parser.add_argument('--attach-pdf', action='store_true', help='Adjuntar también versión PDF (requiere reportlab)')
    parser.add_argument('--smtp-server', default=None, help='Servidor SMTP (si no hay sendmail)')
    parser.add_argument('--smtp-port', type=int, default=0, help='Puerto SMTP (465 SSL, 587 STARTTLS)')
    parser.add_argument('--smtp-user', default=None, help='Usuario SMTP')
    parser.add_argument('--smtp-pass', default=None, help='Contraseña SMTP')
    parser.add_argument('--lines', type=int, default=500, help='Número de líneas a recuperar del journal')
    args = parser.parse_args()

    report_text = build_report()
    out_path = args.output
    Path(out_path).write_text(report_text)

    pdf_path = None
    if args.attach_pdf:
        pdf_path = out_path + '.pdf'
        try:
            generate_pdf(report_text, pdf_path)
        except Exception as e:
            print(f'Error generando PDF: {e}', file=sys.stderr)
            pdf_path = None

    recipients = [r.strip() for r in args.to.split(',') if r.strip()]
    msg = make_email(args.subject, args.sender, recipients, report_text, attach_path=out_path, attach_pdf=pdf_path)

    ok, info = send_email(msg, smtp_server=args.smtp_server, smtp_port=args.smtp_port, smtp_user=args.smtp_user, smtp_pass=args.smtp_pass)
    if ok:
        print('Correo enviado:', info)
    else:
        print('Error enviando correo:', info, file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
