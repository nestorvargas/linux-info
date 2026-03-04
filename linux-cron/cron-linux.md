# Cron y crontab — guía rápida y ejemplos

`cron` es el demonio que ejecuta tareas programadas en sistemas Unix/Linux. `crontab` es la utilidad para editar la tabla de tareas por usuario.

## Archivos y ubicaciones relevantes
- `/etc/crontab` — crontab del sistema (incluye campo de usuario).
- `/etc/cron.d/` — directorio con archivos tipo crontab del sistema.
- `/etc/cron.hourly/`, `/etc/cron.daily/`, `/etc/cron.weekly/`, `/etc/cron.monthly/` — scripts ejecutados por `run-parts`.
- `crontab -e` — editar crontab del usuario actual.
- `crontab -l` — listar crontab del usuario.
- `crontab -r` — eliminar crontab del usuario.

## Formato de una línea en crontab (por usuario)

```
# m h dom mon dow command
```

- `m` = minuto (0-59)
- `h` = hora (0-23)
- `dom` = día del mes (1-31)
- `mon` = mes (1-12 o nombres)
- `dow` = día de la semana (0-7, 0 y 7 = domingo, o nombres)

Campos separados por espacios; `command` puede incluir redirecciones o invocar scripts.

Wildcards y atajos:
- `*` = cualquier valor
- `*/5` = cada 5 unidades (ej. cada 5 minutos)
- Listas: `1,15,30`
- Rangos: `1-5`
- Atajos: `@reboot`, `@hourly`, `@daily`, `@weekly`, `@monthly`, `@yearly`, `@midnight`

## Variables útiles en crontab
- `SHELL=/bin/bash` — shell por defecto para ejecutar comandos.
- `PATH=` — asegurar que el PATH incluye binarios usados por los jobs.
- `MAILTO=` — destinatario para la salida por correo (vacío para deshabilitar).

Ejemplo de encabezado en `crontab -e`:

```
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=admin@example.com
```

## Ejemplos comunes

- Ejecutar script cada 5 minutos:

```
*/5 * * * * /usr/local/bin/mi-script.sh >> /var/log/mi-script.log 2>&1
```

- Ejecutar todos los días a las 2:30:

```
30 2 * * * /opt/mi-app/venv/bin/python /opt/mi-app/backup.py
```

- Ejecutar cada lunes a las 03:00:

```
0 3 * * 1 /usr/local/bin/limpieza-semanal.sh
```

- Ejecutar al arrancar el sistema (`@reboot`):

```
@reboot /opt/mi-app/venv/bin/python /opt/mi-app/run.py >> /var/log/mi-app.log 2>&1
```

- Ejecutar cada 15 minutos durante horas de trabajo (8-18):

```
*/15 8-18 * * * /usr/local/bin/monitor.sh
```

- Ejecutar último día del mes (truco):

```
59 23 28-31 * * [ "$(date +\%d -d tomorrow)" = "01" ] && /usr/local/bin/fin-de-mes.sh
```

## Evitar solapamientos y asegurar exclusión (flock)
Para evitar que la misma tarea se ejecute si la anterior sigue corriendo, usar `flock`:

```
*/5 * * * * /usr/bin/flock -n /var/lock/mi-script.lock /usr/local/bin/mi-script.sh
```

o dentro del script usar `flock` en el descriptor.

## Ejecutar scripts en entorno virtual (Python)
Ejemplo en `crontab -e` para activar venv y ejecutar script:

```
SHELL=/bin/bash
PATH=/opt/mi-app/venv/bin:/usr/bin:/bin
*/30 * * * * /opt/mi-app/venv/bin/python /opt/mi-app/run.py --arg valor >> /var/log/mi-app.log 2>&1
```

También puedes llamar a un wrapper que active el venv:

```sh
#!/bin/bash
source /opt/mi-app/venv/bin/activate
exec python /opt/mi-app/run.py
```

y en crontab: `*/30 * * * * /opt/mi-app/run-wrapper.sh` (asegúrate de `chmod +x`).

## System-wide crontab (`/etc/crontab`)
Formato similar pero incluye campo `user` antes del comando:

```
# m h dom mon dow user command
```

Ejemplo:

```
0 4 * * * root run-parts /etc/cron.daily
```

## Anacron
`anacron` asegura ejecución de tareas diarias/semana/mes en sistemas que no están siempre encendidos (ej. laptops). Normalmente complementa a `cron` en `/etc/anacrontab`.

## Debug y troubleshooting
- Ver logs de salida: si `MAILTO` no está configurado, redirige a fichero con `>> /var/log/job.log 2>&1`.
- Ver si `cron` está activo:

```sh
sudo systemctl status cron    # Debian/Ubuntu
sudo systemctl status crond   # CentOS/RHEL
```

- Forzar una ejecución manual para probar comando.
- Comprobar permisos y PATH (las variables de entorno son limitadas en cron).

## Buenas prácticas
- Usar rutas absolutas en comandos.
- Definir `PATH` en la cabecera si ejecutas binarios no estándar.
- Redirigir salida estándar y errores a logs rotados (logrotate).
- Usar `flock` o mecanismos de locking para evitar concurrencia.
- Para tareas críticas, enviar notificaciones por correo o integrar con monitoring.

---

Si quieres, puedo:
- añadir plantillas de `crontab` para tareas comunes (backup, limpieza, monitorización),
- crear un pequeño script que valide una crontab (formato y permisos),
- o generar ejemplos adaptados a `login_report.py` y `critical_report.py`.
