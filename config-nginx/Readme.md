# config-nginx — QA Multi-proyecto

Configuración Nginx para servidor QA con 14 proyectos: 13 Drupal 11 y 1 Angular SPA + Drupal backend.

**Servidor:** `10.0.64.53` · Nginx + PHP-FPM 8.3 · Oracle Linux 8.4

## Archivos

| Archivo | Descripción |
|---|---|
| `sites-qa.conf` | Configuración Nginx — un `server {}` para todos los proyectos |
| `qa-status.html` | Reporte visual de estado de los 14 sitios |
| `qa-status.pdf` | Reporte PDF generado desde el HTML |

## Proyectos configurados

### Drupal 11 (13 sitios)

Todos sirven desde `/var/www/vhost/<proyecto>/web/` bajo la ruta `http://10.0.64.53/<proyecto>/`.

| Proyecto | Estado |
|---|---|
| dongfeng | 200 OK |
| akt-motos | 302 → Login |
| ganaconkalley | 200 OK |
| invoice | 200 OK |
| kalleymovil | 200 OK |
| knowledgebase | 302 → Login |
| landingdescargas | 200 OK |
| midia | 200 OK |
| narinenseslomaximo | 200 OK |
| pidetucita_alkomprar | 200 OK |
| redcontigo | 200 OK |
| servicios_kalley | 200 OK |
| servicios_tcl | 200 OK |

### Angular SPA + Drupal (1 sitio)

| Proyecto | Ruta SPA | Ruta Drupal |
|---|---|---|
| corbeta_textiles | `/corbeta_textiles/` | `/corbeta_textiles/drupal/` |

## Ajustes aplicados

- `trusted_host_patterns` con IP del servidor QA en `settings.php`
- Seckit desactivado (desactiva HSTS y CSP `upgrade-insecure-requests`)
- MIME type correcto para CSS/JS via `alias` con captura de nombre de archivo
- Redirect automático `/proyecto` → `/proyecto/`
- Workaround para assets con rutas absolutas (`/themes/`, `/core/`, `/modules/`)
- Angular: `sub_filter` para reescribir `<base href="/">` → `<base href="/corbeta_textiles/">`

## Despliegue en servidor

```bash
scp config-nginx/sites-qa.conf drupal@10.0.64.53:/tmp/sites_qa.conf
ssh drupal@10.0.64.53 "sudo cp /tmp/sites_qa.conf /etc/nginx/conf.d/sites/sites_qa.conf && sudo nginx -t && sudo systemctl reload nginx"
```
