# Curso Linux — Contenido del repositorio

Este repositorio contiene notas, ejemplos y scripts para administración, monitorización y hardening en Linux. Abajo tienes la Tabla de Contenidos con enlaces a las carpetas y archivos principales.

## Tabla de Contenidos

- **procesos-linux/**
  - [Comandos y gestión de procesos](procesos-linux/linux-commands-process.md)
  - [Crear servicio (systemd)](procesos-linux/create-service.md)
  - [login_report.py — reporte de inicios de sesión](procesos-linux/login_report.py)
  - [critical_report.py — reporte de fallos críticos](procesos-linux/critical_report.py)
  - [Instrucciones rápidas para login_report](procesos-linux/README-login-report.md)

- **Seguridad-linux/**
- **Seguridad-linux/**
  - [Hardening sysctl (kernel)](Seguridad-linux/linux-kernel-sysctl-hardening.md)
  - [Nginx notes](Seguridad-linux/nginx.md)
  - [Seguridad: resumen](Seguridad-linux/README.md)

-- **service-linux/**
  - [Configurar servicio Python](service-linux/config-service-py.md)
  - [Plantilla: mi-app.service](service-linux/mi-app.service)
  - [Plantilla: mi-app.env](service-linux/mi-app.env)

-- **linux-cron/**
  - [Guía de cron y crontab](linux-cron/cron-linux.md)

-- **ansible-linux/**
  - [Ansible: instalación y ejemplos de despliegue](ansible-linux/ansible-docs.md)

-- **std-linux/**
  - [stdin/stdout/stderr y redirecciones](std-linux/commands-linux.md)

## Uso rápido
- Ve a `procesos-linux/` para scripts operativos y ejemplos de monitorización.
- Revisa `Seguridad-linux/linux-kernel-sysctl-hardening.md` para recomendaciones de `sysctl`.
