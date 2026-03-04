# Entrada/Salida estándar y redirecciones en shell

Breve referencia sobre `stdin`/`stdout`/`stderr` y redirecciones comunes en shells POSIX/Bash, con ejemplos prácticos.

## Conceptos básicos
- `stdin` (descriptor 0): entrada estándar (por defecto teclado).
- `stdout` (descriptor 1): salida estándar (por defecto pantalla).
- `stderr` (descriptor 2): salida de error (por defecto pantalla), separada de `stdout`.

## Redirecciones simples
- Enviar `stdout` a un fichero (sobrescribe):

```sh
comando > salida.txt
```

- Añadir `stdout` a un fichero (append):

```sh
comando >> salida.txt
```

- Enviar `stderr` a un fichero:

```sh
comando 2> errores.txt
```

- Enviar `stderr` a `stdout` (redirigir errores donde va la salida):

```sh
comando 2>&1
```

- En Bash puedes usar atajo `&>` para redirigir `stdout` y `stderr` al mismo fichero (sobrescribe):

```sh
comando &> todo.txt
```

Nota: el orden importa. `comando 2>&1 > salida.txt` no tiene el mismo efecto que `comando > salida.txt 2>&1`.

Ejemplo correcto (redirigir ambos a `salida.txt`):

```sh
comando > salida.txt 2>&1
```

## Piping y combinar con redirecciones
- Una tubería (`|`) pasa sólo `stdout` al siguiente proceso:

```sh
grep error archivo.log | wc -l
```

- Para pasar ambos (`stdout`+`stderr`) por la tubería:

```sh
comando 2>&1 | otra_comando
# o en Bash moderno
comando |& otra_comando
```

Ejemplo: filtrar tanto salida como errores

```sh
./script.sh 2>&1 | tee salida_y_errores.log | grep -i fail
```

## Enviar salida a /dev/null (silenciar)

```sh
comando > /dev/null 2>&1   # descartar stdout y stderr
comando 2> /dev/null       # descartar solo stderr
```

## Capturar salida en variable (incluyendo errores)

```sh
out=$(comando 2>&1)
# ahora $out contiene stdout y stderr mezclados
```

## Usar `tee` para ver y guardar simultáneamente

```sh
comando 2>&1 | tee /var/log/mi-comando.log
```

## Redirecciones en scripts (usar `exec`)
- Redirigir todo el script a fichero de log desde el principio:

```sh
#!/bin/bash
exec > /var/log/mi-script.log 2>&1
echo "inicio"
# todo lo que haga el script irá al log
```

## Here-documents y here-strings

```sh
cat <<EOF > archivo.txt
Línea 1
Línea 2
EOF

grep "patrón" <<< "texto en una sola línea"  # here-string
```

## Redirigir descriptores arbitrarios

```sh
# duplicar fd3 a un archivo
exec 3> /tmp/salida_fd3
echo "hola" >&3
exec 3>&-   # cerrar fd3
```

## Buenas prácticas y ejemplos comunes
- Siempre usar rutas absolutas en scripts ejecutados por cron o systemd.
- Para capturar errores y salida juntos en logs: `comando > /var/log/mi.log 2>&1` o `comando &>> /var/log/mi.log` (append en Bash).
- Para debugging rápido: `comando 2>&1 | sed -n '1,200p'` o usar `tee`.
- En pipelines complejos, recuerda el orden de las redirecciones y prueba los comandos por separado.

---

Si quieres, puedo añadir ejemplos específicos para `systemd` unit files (cómo configurar `StandardOutput`/`StandardError`) o ejemplos de uso en `cron`.

## Ejemplos para `systemd` y `crontab`

### `systemd` — `StandardOutput` / `StandardError`
En unit files de `systemd` puedes controlar la salida con estas opciones en la sección `[Service]`:

```ini
[Service]
ExecStart=/opt/mi-app/venv/bin/python /opt/mi-app/run.py
StandardOutput=journal             # enviar stdout al journal (por defecto)
StandardError=inherit              # heredado de stdout (por defecto), o 'journal', 'null', archivo
# Para redirigir a un fichero (systemd >= v236):
StandardOutput=append:/var/log/mi-app/out.log
StandardError=append:/var/log/mi-app/err.log
```

Notas:
- `journal` envía la salida al journalctl; es lo más común en servicios modernos.
- `append:` escribe en el fichero indicado (requiere systemd con soporte). Asegura permisos y propietario del fichero.
- `Null` o `null` descarta la salida.

Ejemplo de unit con configuración de logging mínima:

```ini
[Unit]
Description=Mi servicio

[Service]
User=miusuario
WorkingDirectory=/opt/mi-app
ExecStart=/opt/mi-app/venv/bin/python /opt/mi-app/run.py
StandardOutput=append:/var/log/mi-app/mi-app.log
StandardError=inherit

[Install]
WantedBy=multi-user.target
```

Para ver logs en el journal:

```sh
sudo journalctl -u mi-app.service -f
```

### `crontab` — ejemplos que usan redirecciones
Ejemplo: ejecutar script y guardar stdout y stderr en un log (append), rotado posteriormente con `logrotate`:

```sh
0 1 * * * /opt/curso-linux/procesos-linux/venv/bin/python /opt/curso-linux/procesos-linux/login_report.py --output /var/reports/login_report_$(date +\%F).pdf >> /var/log/login_report.log 2>&1
```

Ejemplo: ejecutar `critical_report.py` y enviar solo errores por correo (si `MAILTO` está configurado, stdout puede ir al log y stderr se enviará por correo):

```sh
MAILTO=admin@example.com
0 3 * * * /usr/bin/env python3 /opt/curso-linux/procesos-linux/critical_report.py --attach-pdf >> /var/log/critical_report.log 2>/var/log/critical_report.err
```

Ejemplo: silenciar completamente un job en cron:

```sh
0 4 * * * /usr/local/bin/tarea_secreta.sh > /dev/null 2>&1
```

Recuerda que crontab ejecuta en un entorno limitado: usa rutas absolutas y configura `PATH` o activa el `venv` en un wrapper script.


