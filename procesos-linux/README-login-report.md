# login_report

Script para generar un reporte en PDF con el número de inicios de sesión por usuario, usando la salida del comando `last`.

Instrucciones rápidas:

1. Instalar dependencias:

```bash
python3 -m pip install -r requisitos
```

o con el archivo proporcionado:

```bash
python3 -m pip install -r requirements.txt
```

2. Ejecutar:

```bash
python3 login_report.py --output reporte_logins.pdf
```

El script generará `reporte_logins.pdf` en el directorio actual.

Notas:
- El script usa `last` para obtener los inicios de sesión; debe ejecutarse en un sistema Linux con `last` disponible.
- Para analizar logs más antiguos o más detalles (filtrar por rango de fechas, leer `auth.log`), puedo ampliar el script.
