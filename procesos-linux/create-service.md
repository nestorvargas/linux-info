# Crear un servicio en Linux (systemd)

Esta guía explica cómo crear, habilitar y gestionar servicios con `systemd` usando `systemctl` y archivos unit.

## Ubicación de los unit files
- Sistema: `/etc/systemd/system/` (unidades administradas por el administrador)
- Usuario: `~/.config/systemd/user/` (unidades por usuario)

Los archivos también pueden venir del paquete en `/lib/systemd/system/`.

## Estructura mínima de un `service` unit

Ejemplo: `/etc/systemd/system/mi-servicio.service`

```ini
[Unit]
Description=Mi servicio de ejemplo
After=network.target

[Service]
Type=simple
User=miusuario
WorkingDirectory=/opt/mi-app
ExecStart=/usr/bin/python3 /opt/mi-app/run.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Campos importantes:
- `Description`: descripción legible.
- `After` / `Requires`: dependencias de orden/arranque.
- `Type`: `simple` (por defecto), `forking`, `oneshot`, `notify`, `idle`.
- `User` / `Group`: ejecutar como usuario no root para seguridad.
- `ExecStart`: comando a ejecutar (ruta absoluta).
- `Restart` / `RestartSec`: política de reintentos.
- `WantedBy`: target en que se habilita (p. ej. `multi-user.target`).

## Crear y poner en marcha

1. Crear el archivo unit en `/etc/systemd/system/mi-servicio.service`.
2. Recargar daemons:

```sh
sudo systemctl daemon-reload
```

3. Iniciar y comprobar estado:

```sh
sudo systemctl start mi-servicio
sudo systemctl status mi-servicio
journalctl -u mi-servicio -f
```

4. Habilitar al arranque:

```sh
sudo systemctl enable mi-servicio
```

## Editar sin tocar el archivo original (drop-in)
Para cambiar opciones sin modificar el unit file instalado, crear un drop-in:

```sh
sudo systemctl edit mi-servicio
```

Esto abre un archivo en `/etc/systemd/system/mi-servicio.service.d/override.conf` donde puedes poner solo las líneas que quieras cambiar.

## Seguridad y aislamiento (opciones recomendadas)
- `User=` y `Group=`: no ejecutar como `root` si no es necesario.
- `PrivateTmp=yes`: espacio temporal aislado.
- `ProtectSystem=full`: protección del sistema de ficheros.
- `ProtectHome=yes`: restringe acceso a `/home`.
- `NoNewPrivileges=yes`: evita elevación de privilegios.
- `CapabilityBoundingSet=`: limitar capacidades POSIX.
- `RestrictAddressFamilies=`: limitar familias de sockets.

Ejemplo con opciones de seguridad:

```ini
[Service]
User=miusuario
PrivateTmp=yes
ProtectSystem=full
ProtectHome=yes
NoNewPrivileges=yes
CapabilityBoundingSet=CAP_NET_BIND_SERVICE CAP_SYSLOG
```

## Timers (ejecutar periódicamente)
En lugar de `cron`, se puede usar un `timer` de systemd. Ejemplo mínimo:

`/etc/systemd/system/mi-tarea.timer`
```ini
[Unit]
Description=Timer para mi tarea

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`/etc/systemd/system/mi-tarea.service`
```ini
[Unit]
Description=Tarea periódica

[Service]
Type=oneshot
ExecStart=/usr/local/bin/mi-script.sh
```

Habilitar y arrancar:

```sh
sudo systemctl daemon-reload
sudo systemctl enable --now mi-tarea.timer
sudo systemctl list-timers
```

## Transient services
Para lanzar un servicio temporal sin crear archivos:

```sh
sudo systemd-run --unit=temporal --scope /usr/bin/mi-comando
```

## Troubleshooting
- Ver estado y logs:

```sh
sudo systemctl status mi-servicio
journalctl -u mi-servicio -b
```

- Forzar recarga de unidades después de cambios:

```sh
sudo systemctl daemon-reload
sudo systemctl restart mi-servicio
```

- Ver unidades fallidas:

```sh
sudo systemctl --failed
```

## Buenas prácticas
- Comprueba `ExecStart` usando rutas absolutas y permisos.
- No confiar en `Restart=always` sin límites—usa `RestartSec` y `StartLimitBurst`/`StartLimitIntervalSec` si es necesario.
- Registrar la salida estándar y de errores a journal (es default). Para logs adicionales, configura `StandardOutput`/`StandardError`.
- Documenta las dependencias `After` y `Requires` para evitar condiciones de carrera en el arranque.

---

Si quieres, puedo:
- añadir una plantilla de `service` específicamente para `login_report.py` o `critical_report.py`,
- crear la unidad `timer` y `service` automáticamente aquí en el repositorio,
- o generar ejemplos de `drop-in` para añadir opciones de seguridad.
