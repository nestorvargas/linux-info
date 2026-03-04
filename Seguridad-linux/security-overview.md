# Seguridad en Linux — Resumen y buenas prácticas

Este documento resume prácticas y controles básicos para mejorar la seguridad de servidores Linux. Está pensado como guía rápida y referencia; si quieres, puedo ampliar cada sección con ejemplos concretos (playbooks Ansible, unidades systemd, scripts, etc.).

1. Actualizaciones y parches
- Mantén el sistema actualizado: `apt update && apt upgrade` o `dnf update` según la distro.
- Automatiza actualizaciones de seguridad o planifica ventanas de mantenimiento.

2. Usuarios y control de acceso
- Evita usar `root` para tareas diarias. Usa `sudo` con configuraciones restrictivas en `/etc/sudoers.d/`.
- Revisa cuentas inactivas y elimina usuarios innecesarios.
- Enforce password policies (pam_pwquality, uso de `chage`).

3. SSH
- Deshabilita login por contraseña y usa `PubkeyAuthentication yes`.
- Cambia el puerto por defecto solo como medida adicional (no suficiente por sí sola).
- Restringe accesos por `AllowUsers` / `AllowGroups` y usa `Match` para reglas por red.
- Deshabilita `PermitRootLogin`.

4. Firewall y control de red
- Usa `nftables` o `iptables`/`ufw` para permitir solo puertos necesarios.
- Registra y monitoriza conexiones inusuales (fail2ban puede bloquear intentos repetidos).

5. Hardening del kernel y parámetros de red
- Revisa y aplica recomendaciones en `linux-kernel-sysctl-hardening.md` (controversias y valores según carga).
- Ejemplos útiles: desactivar IP forwarding si no se necesita, hardening de ICMP, syn cookies.

6. Servicios mínimos y privilegios
- Ejecuta servicios con cuentas dedicadas y sin más privilegios de los necesarios.
- Usa `NoNewPrivileges=yes`, `PrivateTmp=yes`, `ProtectSystem=strict` en unidades systemd.

7. Logs, auditoría y rotación
- Habilita `rsyslog`/`systemd-journald` según necesidades; rota logs con `logrotate`.
- Activa `auditd` para auditoría de eventos críticos y revisa reglas.

8. Detección y respuesta
- Instala herramientas de detección: `fail2ban`, `OSSEC`, `Wazuh`, EDR según presupuesto.
- Define procedimientos de respuesta (playbooks) para incidentes críticos.

9. Protección de archivos y permisos
- Usa `chmod`/`chown` correctos en ficheros sensibles (/etc/shadow, claves privadas).
- Implementa controles de integridad (AIDE, tripwire).

10. Contenedores y aislamiento
- Para entornos con contenedores, sigue prácticas específicas: no correr contenedores como root, limitar recursos, usar seccomp/AppArmor/SELinux profiles.

11. Copias de seguridad y pruebas de restauración
- Define políticas de backup y prueba regularmente las restauraciones.

12. Checklist rápido (comandos)
- Actualizar sistema: `sudo apt update && sudo apt upgrade -y`
- Comprobar cuentas con shell: `awk -F: '($7!="/sbin/nologin" && $7!="/bin/false"){print $1}' /etc/passwd`
- Revisar SSH: `sudo ss -tulpen | grep sshd` y `sudo cat /etc/ssh/sshd_config | grep -E "PermitRootLogin|PasswordAuthentication|PubkeyAuthentication"`
- Revisar servicios fallidos: `systemctl --failed`
- Reglas iptables/nft: `sudo nft list ruleset` or `sudo iptables -L -n -v`

Referencias y lecturas recomendadas
- CIS Benchmarks (por distro)
- OWASP Server Hardening notes
- Documentación de `systemd`, `auditd`, `fail2ban`.

Si quieres que amplíe alguna sección (por ejemplo: playbook Ansible para aplicar sysctl, plantilla `audit.rules`, o una guía paso a paso para asegurar SSH), dime cuál y lo desarrollo.
