# Apps y herramientas para pruebas de seguridad (resumen)

Versión extendida: [apps-probe-security-extended.md](apps-probe-security-extended.md)

Lista breve y directa de herramientas usadas para pruebas de carga, enumeración, escaneo y discovery. Si necesitas más detalle por herramienta, avísame y lo amplio.

## Rápido: comandos ejemplo

- `nmap -sV -A ejemplo.com` — escaneo de servicios y versiones.
- `nikto -h ejemplo.com` — escaneo web básico.
- `ffuf -u https://ejemplo.com/FUZZ -w wordlist.txt` — fuzzing de rutas.
- `siege -b -r 1 -c 10 -v https://ejemplo.com` — prueba de carga básica.

## Herramientas mencionadas

- Slowloris — probar agotamiento de conexiones (DDoS a nivel de aplicación).
- Apache JMeter — pruebas de carga y generación de informes.
- Git tools (gitdumper, etc.) — recolección de contenido expuesto en `/.git/`.
- Burp Suite — proxy/interceptor para auditoría manual y testing.
- OWASP ZAP — alternativa open-source a Burp para DAST.
- testssl.sh / SSL Test — pruebas sobre TLS/SSL y configuraciones inseguras.
- Dirb / Gobuster — fuerza bruta de directorios y ficheros en aplicaciones web.
- Dropscan — escaneo automatizado de CMS (Drupal, Joomla, WordPress).

---

Para la lista extendida y ejemplos, revisa `apps-probe-security-extended.md`.
