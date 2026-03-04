# systemd — unidades de ejemplo

Archivos de ejemplo para instalar un `service` y un `timer` que ejecuten `critical_report.py` diariamente.

Archivos incluidos:
- `critical_report.service` — unidad `oneshot` que ejecuta el script.
- `critical_report.timer` — timer que activa la unidad diariamente a las 03:00.

Instalación (como root):

```sh
# Copiar unit y timer al directorio system
sudo cp critical_report.service /etc/systemd/system/
sudo cp critical_report.timer /etc/systemd/system/

# Crear archivo de configuración con destinatarios
sudo tee /etc/default/critical_report > /dev/null <<'EOF'
# variables de configuración utilizadas por el unit
RECIPIENTS="admin@example.com"
# Opcional: SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASS
EOF

# Recargar systemd, habilitar y arrancar el timer
sudo systemctl daemon-reload
sudo systemctl enable --now critical_report.timer

# Ver estado
sudo systemctl list-timers --all
sudo systemctl status critical_report.timer
sudo journalctl -u critical_report.service -f
```

Notas:
- Ajusta `WorkingDirectory` y `ExecStart` en `critical_report.service` al path donde se instale el script en el servidor (p. ej. `/opt/curso-linux/procesos-linux`).
- Para ejecutar con un usuario no-root, cambia `User=` y asegúrate de que tenga permisos para leer logs y ejecutar `journalctl` si es necesario.
- Para probar manualmente la unidad: `sudo systemctl start critical_report.service`.
