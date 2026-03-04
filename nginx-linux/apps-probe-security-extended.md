# Apps y herramientas para pruebas y probe de seguridad

Lista de herramientas usadas para pruebas de carga, enumeración, escaneo y discovery. Incluye comandos ejemplo mínimos.

## Herramientas ya mencionadas

- Slowloris — herramienta para probar agotamiento de conexiones (DDoS a nivel de aplicación).
- Apache JMeter — pruebas de carga y generación de informes.
- Git tools (gitdumper, etc.) — recolección de contenido expuesto en `/.git/`.

Ejemplo de uso de `gitdumper`:

```bash
./gitdumper.sh https://asesores.alkomprar.com/.git/ AsesoresAlkomprar
```

- `nmap -sV -A ejemplo.com` — escaneo de servicios y detección de versiones.

- Burp Suite — proxy/interceptor para auditoría manual y testing.
- OWASP ZAP — alternativa open-source a Burp para DAST.
- testssl.sh / SSL Test — pruebas sobre TLS/SSL y configuraciones inseguras.
- Dirb / Gobuster — fuerza bruta de directorios y ficheros en aplicaciones web.
- Siege — herramienta de carga: `siege -b -r 1 -c 10 -v https://ejemplo.com`
- Dropscan — escaneo automatizado de CMS (Drupal, Joomla, WordPress).
- Nikto — escáner web básico: `nikto -h ejemplo.com`

---

## Herramientas recomendadas adicionales (por categoría)

### Descubrimiento y enumeración
- `amass` — descubrimiento de subdominios y mapeo de infraestructura.

```bash
amass enum -d ejemplo.com -o amass-subdomains.txt
```

- `subfinder` / `assetfinder` — descubrimiento rápido de subdominios.
- `theHarvester` — recolección de correos, subdominios y hosts desde fuentes públicas.

### Escaneo de red y puertos
- `masscan` — escaneo masivo de puertos (muy rápido).

```bash
sudo masscan 0.0.0.0/0 -p80,443 --rate=1000
```

- `nmap` + scripts NSE — escaneo avanzado y detección de servicios.

### Escaneo de vulnerabilidades
- `OpenVAS / Greenbone` — scanner de vulnerabilidades completo.
- `Nessus` — scanner comercial muy usado.

### Escaneo web / DAST y fuzzing
- `sqlmap` — detección y explotación automatizada de SQLi.
- `ffuf` / `gobuster` — fuerza bruta de directorios/archivos y fuzzing.

```bash
ffuf -u https://ejemplo.com/FUZZ -w wordlist.txt
```

- `wpscan` — escáner para WordPress.
- `testssl.sh` / `sslyze` — pruebas TLS/SSL.

### Proxy / Interceptores
- `Burp Suite` — proxy, escaneo y herramientas manuales.
- `OWASP ZAP` — proxy/interceptor open-source.

### Fingerprinting / WAF
- `wafw00f` — detecta WAFs y protecciones.
- `whatweb` — fingerprinting de tecnologías.

### Fuerza bruta / autenticación
- `hydra`, `medusa`, `patator` — ataques contra servicios (ssh, ftp, http-form).
- `john`, `hashcat` — crackeo de hashes.

### SAST / análisis de código y secretos
- `semgrep` — reglas de seguridad para código.
- `bandit` — análisis de seguridad para Python.
- `gitleaks`, `truffleHog` — búsqueda de secretos en repositorios.

### Contenedores / Kubernetes
- `trivy` — escaneo rápido de imágenes y filesystem.
- `kube-bench`, `kube-hunter` — auditoría y escaneo de clusters Kubernetes.

### Detección / IDS / análisis de red
- `suricata`, `snort` — IDS/IPS de red.
- `zeek` — análisis de tráfico de red.

### Fuzzing y pruebas avanzadas
- `AFL` (American Fuzzy Lop) — fuzzer binario.
- `Boofuzz` — fuzzing de protocolos.

### Cloud / auditoría
- `prowler` (AWS), `ScoutSuite`, `Cloud Custodian` — auditoría de configuraciones cloud.

---

Si quieres, puedo:

- convertir esto en una hoja de referencia (`Seguridad-linux/tools-cheat-sheet.md`) con enlaces oficiales y comandos de instalación por distro;
- añadir instrucciones de instalación (apt, dnf, brew) y ejemplos concretos para las herramientas que más te interesen;
- o bien crear playbooks Ansible para desplegar las herramientas en un host de pruebas.

Dime qué prefieres y lo continuo.
