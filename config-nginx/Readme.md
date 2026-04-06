# config-nginx — QA Multi-proyecto

Configuración Nginx para servidor QA con 14 proyectos: 13 Drupal 11 y 1 Angular SPA + Drupal backend.
Cada proyecto tiene su propio archivo `server {}` completamente independiente.

**Servidor:** `10.0.64.53` · Nginx + PHP-FPM 8.3 · Oracle Linux 8.4

---

## Sitios disponibles

| # | Proyecto | Puerto | URL | Tipo | Archivo config |
|---|---|---|---|---|---|
| 1 | dongfeng | 8001 | http://10.0.64.53:8001/ | Drupal 11 | `site-dongfeng-qa.conf` |
| 2 | akt-motos | 8002 | http://10.0.64.53:8002/ | Drupal 11 | `site-akt-motos-qa.conf` |
| 3 | ganaconkalley | 8003 | http://10.0.64.53:8003/ | Drupal 11 | `site-ganaconkalley-qa.conf` |
| 4 | invoice | 8004 | http://10.0.64.53:8004/ | Drupal 11 | `site-invoice-qa.conf` |
| 5 | kalleymovil | 8005 | http://10.0.64.53:8005/ | Drupal 11 | `site-kalleymovil-qa.conf` |
| 6 | knowledgebase | 8006 | http://10.0.64.53:8006/ | Drupal 11 | `site-knowledgebase-qa.conf` |
| 7 | landingdescargas | 8007 | http://10.0.64.53:8007/ | Drupal 11 | `site-landingdescargas-qa.conf` |
| 8 | midia | 8008 | http://10.0.64.53:8008/ | Drupal 11 | `site-midia-qa.conf` |
| 9 | narinenseslomaximo | 8009 | http://10.0.64.53:8009/ | Drupal 11 | `site-narinenseslomaximo-qa.conf` |
| 10 | pidetucita_alkomprar | 8010 | http://10.0.64.53:8010/ | Drupal 11 | `site-pidetucita_alkomprar-qa.conf` |
| 11 | redcontigo | 8011 | http://10.0.64.53:8011/ | Drupal 11 | `site-redcontigo-qa.conf` |
| 12 | servicios_kalley | 8012 | http://10.0.64.53:8012/ | Drupal 11 | `site-servicios_kalley-qa.conf` |
| 13 | servicios_tcl | 8013 | http://10.0.64.53:8013/ | Drupal 11 | `site-servicios_tcl-qa.conf` |
| 14 | corbeta_textiles | 8014 | http://10.0.64.53:8014/ | Angular + Drupal | `site-corbeta_textiles-qa.conf` |

> Puerto 80 (`sites-qa.conf`) muestra el listado de proyectos disponibles.

---

## Estructura de archivos

```
config-nginx/
├── sites-qa.conf                       # Puerto 80 — landing con listado
├── site-dongfeng-qa.conf               # Puerto 8001
├── site-akt-motos-qa.conf              # Puerto 8002
├── site-ganaconkalley-qa.conf          # Puerto 8003
├── site-invoice-qa.conf                # Puerto 8004
├── site-kalleymovil-qa.conf            # Puerto 8005
├── site-knowledgebase-qa.conf          # Puerto 8006
├── site-landingdescargas-qa.conf       # Puerto 8007
├── site-midia-qa.conf                  # Puerto 8008
├── site-narinenseslomaximo-qa.conf     # Puerto 8009
├── site-pidetucita_alkomprar-qa.conf   # Puerto 8010
├── site-redcontigo-qa.conf             # Puerto 8011
├── site-servicios_kalley-qa.conf       # Puerto 8012
├── site-servicios_tcl-qa.conf          # Puerto 8013
├── site-corbeta_textiles-qa.conf       # Puerto 8014 (Angular SPA + /drupal/)
├── qa-status.html                      # Reporte visual de estado
└── qa-status.pdf                       # Reporte PDF
```

---

## Ajustes aplicados

- Cada proyecto corre en su propio puerto — sin rutas compartidas ni variables globales
- `trusted_host_patterns` con IP + puerto en `settings.php` de cada sitio Drupal
- Seckit desactivado en todos los sitios (elimina HSTS y CSP `upgrade-insecure-requests`)
- Image styles: `try_files $uri @php` para generar derivados vía Drupal si no existen
- corbeta_textiles: Angular SPA en `/`, Drupal backend en `/drupal/`

---

## Despliegue en servidor

```bash
# 1. Subir archivos
scp config-nginx/site-*-qa.conf config-nginx/sites-qa.conf drupal@10.0.64.53:/tmp/

# 2. En el servidor
sudo cp /tmp/site-*-qa.conf /tmp/sites-qa.conf /etc/nginx/conf.d/sites/

# 3. Abrir puertos en el firewall
sudo firewall-cmd --permanent --add-port=8001-8014/tcp
sudo firewall-cmd --reload

# 4. Validar y recargar nginx
sudo nginx -t && sudo systemctl reload nginx
```
