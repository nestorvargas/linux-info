# Comandos para revisar, pausar y terminar procesos

Este documento recoge comandos y ajustes comunes para **revisar**, **pausar/reanudar** y **terminar** procesos en Linux. Incluye ejemplos prácticos y buenas prácticas.

## Revisar procesos
- Listar procesos (información básica):

```sh
ps aux
```

- Buscar procesos por nombre o patrón:

```sh
ps aux | grep nombre_proceso
pgrep -a nombre_parcial
pidof nombre_proceso
```

- Ver uso en tiempo real:

```sh
top
# o, si está instalado
htop
```

- Mostrar árbol de procesos:

```sh
pstree -p
```

- Información detallada de un PID:

```sh
ls -l /proc/<PID>
cat /proc/<PID>/status
cat /proc/<PID>/cmdline
lsof -p <PID>
strace -p <PID>    # solo para diagnóstico (requiere permisos)
```

## Pausar y reanudar procesos
- Control de trabajos en la shell (procesos iniciados desde la misma terminal):

```sh
# Suspender con Ctrl+Z (envía SIGTSTP)
jobs             # listar trabajos en background/suspendidos
bg %1            # continuar en background
fg %1            # llevar trabajo al foreground
```

### Comando `jobs` (detallado)
`jobs` muestra el estado de los trabajos gestionados por la shell interactiva (foreground/background).

Opciones y uso:

```sh
jobs                 # lista trabajos con su estado (Stopped, Running, Done)
jobs -l              # muestra PID junto al número de trabajo
jobs -p              # muestra solo PIDs
```

Etiquetas y selectores de trabajo:
- `%n`  — el trabajo con número `n` (ej. `%1`).
- `%%` o `%+` — el trabajo actual (el más reciente).
- `%-` — el trabajo previo al actual.

Ejemplos prácticos:

```sh
sleep 300 &          # lanza en background
jobs                 # ver trabajo listado (p. ej. [1]+  Running sleep 300 &)
fg %1                # traer trabajo 1 al foreground
bg %1                # asegurar que continúa en background
jobs -l              # ver PID si necesitas usar kill

# iniciar y descartar de la tabla de jobs para que no cierre al salir de la shell
nohup mi_comando &
disown %1            # elimina el trabajo de la tabla de la shell

# esperar a un job (acepta PID o especificador de job)
wait %1
```

Notas importantes:
- El control de trabajos es una característica de shells interactivas (bash, zsh, etc.). No funciona en shells no interactivos o en procesos remotos sin TTY.
- Los números de trabajo son locales a la sesión de shell y se reinician en cada nueva terminal.
- Usa `disown` o `nohup` si necesitas que el proceso sobreviva al cierre de la sesión.


- Señales para pausar/reanudar por PID:

```sh
kill -STOP <PID>   # pausa (equivalente a SIGSTOP)
kill -CONT <PID>   # reanuda (SIGCONT)
```

- Uso típico: pausar temporalmente para liberar CPU o examinar estado, luego reanudar.

## Terminar procesos
- Señales de terminación más comunes:

```sh
kill -TERM <PID>   # SIGTERM, petición educada de terminación
kill -INT <PID>    # SIGINT, como Ctrl+C
kill -KILL <PID>   # SIGKILL (9), fuerza terminación inmediata
```

- By-name y patrones:

```sh
pkill -f 'patrón'       # mata procesos cuyo cmdline coincide
killall nombre_proceso  # mata por nombre (cuidado con varios usuarios)
```

- Para servicios (systemd):

```sh
sudo systemctl stop nombre_servicio
sudo systemctl status nombre_servicio
```

- Ejecutar con tiempo límite (termina si excede):

```sh
timeout 30s comando_a_ejecutar   # mata el comando tras 30s
```

## Señales útiles y cómo verlas
- Listar señales disponibles:

```sh
kill -l
```

- Señales importantes:
- `SIGTERM` (15): petición de terminación limpia. Puede ser capturada por el proceso para cerrar recursos.
- `SIGKILL` (9): fuerza la terminación inmediata; no puede ser capturada ni ignorada.
- `SIGINT` (2): interrupción (equivalente a Ctrl+C); suele permitir limpieza.
- `SIGHUP` (1): petición de recarga/rehabilitación; usada por demonios para recargar configuración.
- `SIGSTOP` (19) / `SIGTSTP` (20) y `SIGCONT` (18): pausar/resumir procesos; `SIGSTOP` no es capturable.
- `SIGUSR1` / `SIGUSR2`: señales de uso por aplicaciones para acciones definidas por el programa.

### Detalle y ejemplos de uso
- Enviar `SIGTERM` (pedido educado de salida):

```sh
kill -TERM <PID>
# o, equivalente por número
kill -15 <PID>
```

Uso típico: primero intenta `SIGTERM` para permitir que el proceso cierre ficheros, conexiones y guarde estado.

- Forzar con `SIGKILL` cuando `SIGTERM` no funciona:

```sh
kill -KILL <PID>
# o
kill -9 <PID>
```

Precaución: `SIGKILL` no permite limpieza; puede dejar recursos en estado inconsistente.

- Pausar y reanudar:

```sh
kill -STOP <PID>   # pausa (no capturable)
kill -CONT <PID>   # reanuda
```

- Recargar configuración con `SIGHUP` (común en demonios):

```sh
kill -HUP <PID>
# muchos servicios también aceptan 'systemctl reload servicio'
```

- Enviar señales por nombre con `pkill`/`killall`:

```sh
pkill -TERM -f 'mi_proceso'     # envía SIGTERM a procesos cuyo cmdline coincide
pkill -KILL -u usuario mi_proceso
killall -15 nombre_proceso
```

- `timeout` para terminar procesos que exceden tiempo (envía SIGTERM, puede forzar SIGKILL con --kill-after):

```sh
timeout --kill-after=5s 30s mi_comando
```

### Ejemplo: manejar señales en scripts (trap)
Si tu script necesita hacer limpieza al recibir `SIGTERM` o `SIGINT`:

```sh
#!/bin/bash
trap 'echo "Recibí SIGTERM, cerrando..."; cleanup_function; exit 0' SIGTERM SIGINT

cleanup_function() {
	# cerrar conexiones, eliminar ficheros temporales
	echo "Limpiando..."
}

while true; do
	sleep 1
done
```

Cuando este script reciba `SIGTERM` (por ejemplo `kill -TERM <PID>`), ejecutará `cleanup_function` antes de salir.

### Buenas prácticas rápidas
- Intentar `SIGTERM` antes de `SIGKILL` para permitir cierre ordenado.
- No confiar en `SIGKILL` para limpieza de recursos compartidos.
- Documentar qué señales entiende una aplicación (consultar su documentación o código).
- En entornos de producción, preferir `systemctl stop` o `service stop` para servicios gestionados.

## Uso de `less`
`less` es el paginador estándar para ver archivos grandes; soporta búsqueda, navegación y modo "seguir".

Ejemplos básicos:

```sh
less archivo.log
less -N archivo.log        # mostrar números de línea
less -S archivo.log        # cortar líneas largas en lugar de envolver
less -R archivo_coloreado  # respetar secuencias ANSI de color
less +F archivo.log        # seguir la salida (similar a tail -f)
```

Navegación dentro de `less`:
- `space` o `f`: página siguiente
- `b`: página anterior
- `j` / `k`: desplazamiento línea a línea
- `G`: ir al final; `g` al principio
- `/patrón` y `?patrón`: búsqueda hacia adelante/atrás; `n` / `N` para próximos/anteriores
- `:n` o `:<n>`: ir a la línea n
- `m<letra>`: marcar posición; `' <letra>`: volver a la marca

Uso combinado y pipes:

```sh
tail -n 200 /var/log/syslog | less -S
journalctl -u mi-servicio | less -S
gzip -dc archivo.log.gz | less
# o usar zless/zcat/zmore según el sistema
```

Consejos rápidos:
- En modo `+F`, presiona `Ctrl-C` para salir del seguimiento y usar navegación; presiona `F` para volver a seguir.
- `less -X` evita que la pantalla se limpie al salir (útil en algunas terminales).

## Herramientas útiles para administradores Linux
Breve lista de comandos y ejemplos que todo administrador debería conocer.

- `journalctl` — ver logs del systemd:

```sh
journalctl -u nombre_servicio -f    # seguir logs del servicio
journalctl -k -b                    # ver mensajes del kernel desde el arranque
```

- `ss` / `netstat` — sockets y puertos:

```sh
ss -tulnp    # ver puertos en escucha y procesos
ss -s        # resumen
```

- `ip` — gestión de red (reemplaza muchas funciones de `ifconfig`/`route`):

```sh
ip addr show
ip route show
ip link set dev eth0 up/down
```

- `tcpdump` — captura de tráfico (usar filtros):

```sh
sudo tcpdump -i eth0 port 80 -w captura.pcap
```

- `iptables` / `nft` / `ufw` / `firewalld` — firewalling (ejemplos dependiendo del sistema):

```sh
sudo nft list ruleset
sudo iptables -L -n -v
sudo ufw status
sudo firewall-cmd --list-all
```

- `crontab` / `at` — tareas programadas:

```sh
crontab -e
at 02:00 tomorrow -f job.sh
```

- `rsync` / `tar` — copias y backups:

```sh
rsync -avz /origen/ usuario@host:/destino/
tar -czvf backup.tar.gz /ruta/a/respaldar
```

- Almacenamiento y uso de disco:

```sh
df -h
du -sh /var/log
```

- Monitorización y rendimiento:

```sh
top / htop
vmstat 1
iostat -x 1 (si está instalado)
```

- Usuarios y permisos:

```sh
sudo useradd -m usuario
sudo passwd usuario
sudo usermod -aG grupo usuario
sudo chown -R usuario:grupo /ruta
sudo chmod -R 750 /ruta
```

- Arranque y servicios:

```sh
sudo systemctl status servicio
sudo systemctl restart servicio
sudo systemctl enable servicio
```

## Comandos `systemd` (`systemctl`)
`systemd` es el init system más usado; `systemctl` es la herramienta principal para gestionar unidades (services, sockets, timers, etc.).

Operaciones básicas:

```sh
sudo systemctl start nombre.service       # iniciar
sudo systemctl stop nombre.service        # detener
sudo systemctl restart nombre.service     # reiniciar
sudo systemctl reload nombre.service      # recargar configuración sin reiniciar
sudo systemctl status nombre.service      # ver estado y logs resumidos
sudo systemctl enable nombre.service      # habilitar al arranque
sudo systemctl disable nombre.service     # deshabilitar al arranque
```

Comandos útiles de inspección y diagnóstico:

```sh
sudo systemctl is-active nombre.service   # devuelve active/inactive
sudo systemctl is-enabled nombre.service  # enabled/disabled
sudo systemctl --failed                   # listar unidades fallidas
sudo systemctl list-units --type=service  # listar servicios cargados
sudo systemctl show nombre.service        # mostrar propiedades detalladas
sudo systemctl cat nombre.service         # mostrar el unit file (y drop-ins)
```

Logs y manejo de journal:

```sh
journalctl -u nombre.service -f           # seguir logs del servicio
journalctl -b -p err                      # ver errores del arranque actual
```

Gestión avanzada:

```sh
sudo systemctl daemon-reload              # recargar configuraciones de unidades tras cambios de archivos
sudo systemctl mask nombre.service        # impedir que se inicie la unidad (enlace a /dev/null)
sudo systemctl unmask nombre.service
sudo systemctl set-property nombre.service CPUQuota=50%  # ajustar propiedades en tiempo de ejecución
sudo systemctl kill --kill-who=main --signal=SIGTERM nombre.service  # enviar señal a la unidad
```

Timers y sockets:

```sh
sudo systemctl list-timers                # ver timers activos
sudo systemctl start nombre.timer         # iniciar timer (si existe)
```

Buenas prácticas:
- Usa `systemctl status` y `journalctl -u` antes de matar PIDs manualmente.
- Modifica archivos unit en `/etc/systemd/system/` y usa `daemon-reload` tras los cambios.
- Prefiere `reload` cuando la unidad lo soporte para evitar downtime.


- Diagnóstico del kernel y hardware:

```sh
dmesg | less
lsblk
lshw (si está instalado)
```

- SSH y acceso remoto:

```sh
ssh usuario@host
scp archivo usuario@host:/ruta
sshd: sudo systemctl reload sshd  # recargar configuración
```

Si quieres, puedo ampliar cualquiera de estos apartados con ejemplos más detallados (por ejemplo, reglas comunes de `iptables/nft`, ejemplos de `tcpdump` para depuración HTTP, o plantillas de `crontab`).

## Ejemplos prácticos
- Encontrar y matar procesos con alto uso de CPU:

```sh
# Ver procesos ordenados por CPU
ps aux --sort=-%cpu | head -n 10
# Matar el PID problemático (ejemplo)
kill -TERM 12345
```

- Pausar un proceso para inspeccionarlo y luego reanudarlo:

```sh
kill -STOP 23456
# inspeccionar carpetas /proc, lsof, strace...
kill -CONT 23456
```

## Herramientas útiles adicionales
- `htop` (interfaz interactiva), `atop` (histórico), `glances`.
- `strace -p <PID>` para traza de llamadas al sistema (diagnóstico).
- `lsof -p <PID>` para ver archivos y sockets abiertos.

## Buenas prácticas y precauciones
- Intenta siempre `SIGTERM` antes de `SIGKILL` para permitir limpieza.
- Evita `killall` sin confirmar el usuario/alcance en sistemas multiusuario.
- Para servicios, usa las herramientas de init (`systemctl`/`service`) en lugar de matar PIDs manualmente.
- Documenta y anota procesos críticos antes de finalizar cambios en producción.

---

Si quieres, puedo:
- añadir ejemplos más específicos para `systemd` o contenedores (Docker),
- incluir instrucciones para depurar procesos que consumen memoria o sockets.

