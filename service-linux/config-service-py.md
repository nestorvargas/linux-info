# Configurar y ejecutar un servicio Python

Documento breve con pasos y ejemplos para desplegar una aplicación Python como servicio `systemd`, incluyendo archivo de configuración (`EnvironmentFile`) y buenas prácticas.

## Estructura recomendada
- Código de la aplicación: `/opt/mi-app/` (por ejemplo `/opt/curso-linux/procesos-linux`)
- Entorno virtual: `/opt/mi-app/venv`
- Unit file systemd: `/etc/systemd/system/mi-app.service`
- Archivo de configuración de entorno (EnvironmentFile): `/etc/default/mi-app`

## Ejemplo de `EnvironmentFile` (/etc/default/mi-app)
Este archivo contiene variables de entorno y parámetros que la unidad leerá.

```sh
# /etc/default/mi-app
# destinatarios o parámetros para el script
RECIPIENTS="admin@example.com"
# Opcional: ajuste de SMTP
SMTP_SERVER="smtp.example.com"
SMTP_PORT=587
SMTP_USER="user@example.com"
SMTP_PASS="secreto"
# Ruta del intérprete/venv
VENV_PATH="/opt/mi-app/venv"
```

Permisos: restringe lectura a root si contiene secretos:

```sh
sudo chown root:root /etc/default/mi-app
sudo chmod 600 /etc/default/mi-app
```

## Ejemplo de `systemd` unit (usa `EnvironmentFile`)
Colocar en `/etc/systemd/system/mi-app.service`:

```ini
[Unit]
Description=Mi servicio Python
After=network.target

[Service]
Type=simple
User=miusuario
Group=miusuario
WorkingDirectory=/opt/mi-app
EnvironmentFile=/etc/default/mi-app
ExecStart=/opt/mi-app/venv/bin/python /opt/mi-app/run.py --to "$RECIPIENTS"
Restart=on-failure
RestartSec=5
PrivateTmp=yes
ProtectSystem=full
ProtectHome=yes
NoNewPrivileges=yes

[Install]
WantedBy=multi-user.target
```

Notas:
- `EnvironmentFile` acepta `VAR=valor`. Las variables se expanden en `ExecStart` si se usan comillas.
- Usa rutas absolutas en `ExecStart` y asegúrate que el `User` tenga permisos para acceder a los ficheros necesarios.

## Crear el entorno y permisos recomendados

```sh
sudo mkdir -p /opt/mi-app
sudo chown miusuario:miusuario /opt/mi-app
sudo -u miusuario python3 -m venv /opt/mi-app/venv
sudo -u miusuario /opt/mi-app/venv/bin/pip install -r /opt/mi-app/requirements.txt
sudo chmod +x /opt/mi-app/run.py
```

## Recargar, probar y habilitar

```sh
sudo systemctl daemon-reload
sudo systemctl start mi-app.service
sudo systemctl status mi-app.service
sudo journalctl -u mi-app.service -f
sudo systemctl enable mi-app.service
```

## Probar sin instalar el unit (debug rápido)
Ejecuta el comando `ExecStart` manualmente con el mismo entorno para verificar errores:

```sh
/opt/mi-app/venv/bin/python /opt/mi-app/run.py --to "admin@example.com"
```

## Logging y depuración
- Por defecto la salida se envía al `journal` (ver `journalctl -u mi-app`).
- Para logs persistentes, el script puede escribir a ficheros bajo `/var/log/mi-app/` con permisos adecuados.

## Drop-in para cambios rápidos
Para cambiar sólo una opción sin editar el unit original:

```sh
sudo systemctl edit mi-app.service
```

Eso crea `/etc/systemd/system/mi-app.service.d/override.conf` con las modificaciones.

## Seguridad y buenas prácticas
- No ejecutar como `root` salvo necesidad; crea un usuario dedicado.
- Restringe lectura de `/etc/default/mi-app` si contiene secretos.
- Si necesitas recursos de red o permisos especiales, limita capacidades con `CapabilityBoundingSet=`.
- Usa `RestartSec`, `StartLimitBurst` y `StartLimitIntervalSec` para controlar reinicios.

---

Si quieres, puedo:
- generar aquí los archivos `mi-app.service` y `mi-app.env` de ejemplo dentro del repo para que los copies,
- o crear un script que empaquete e instale la unidad automáticamente en el servidor.

## Ejemplos relacionados en este repositorio
Puedes usar los ejemplos ya incluidos en este repositorio como plantilla y referencia:

- Unidad y timer de ejemplo para `critical_report.py`: [procesos-linux/systemd/critical_report.service](procesos-linux/systemd/critical_report.service) y [procesos-linux/systemd/critical_report.timer](procesos-linux/systemd/critical_report.timer) (documentado en [procesos-linux/systemd/README.md](procesos-linux/systemd/README.md)).
- Script de reporte crítico: [procesos-linux/critical_report.py](procesos-linux/critical_report.py)
- Script de reporte de logins: [procesos-linux/login_report.py](procesos-linux/login_report.py) y su README [procesos-linux/README-login-report.md](procesos-linux/README-login-report.md).
- Guía y ejemplos de `cron` y `crontab`: [linux-cron/cron-linux.md](../linux-cron/cron-linux.md)

### Ejemplos rápidos de crontab para estos scripts

Si prefieres usar `cron` en lugar de `systemd` `timer`, aquí tienes ejemplos para `crontab -e` del usuario apropiado (ajusta rutas y `venv`):

- Ejecutar `login_report.py` cada día a las 01:00 y guardar PDF en `/var/reports`:

```
0 1 * * * /opt/curso-linux/procesos-linux/venv/bin/python /opt/curso-linux/procesos-linux/login_report.py --output /var/reports/login_report_$(date +\%F).pdf >> /var/log/login_report.log 2>&1
```

- Ejecutar `critical_report.py` cada día a las 03:00 y enviar por correo (usa `/etc/default/critical_report` para configurar destinatarios):

```
0 3 * * * /usr/bin/env python3 /opt/curso-linux/procesos-linux/critical_report.py --to admin@example.com --attach-pdf >> /var/log/critical_report.log 2>&1
```

Recuerda que en crontab debes usar rutas absolutas y configurar `PATH` o `venv` si tus scripts dependen de entornos virtuales.

---

Si quieres que agregue los archivos `mi-app.service` y `mi-app.env` (plantillas) dentro de `service-linux/` para facilitar copia/edición, lo hago ahora.
