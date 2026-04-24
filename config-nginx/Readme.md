# config-nginx — QA Multi-proyecto

Configuración Nginx para servidor QA con múltiples proyectos bajo un único `server {}` en el puerto 80.
Cada proyecto se sirve bajo su propio subpath (`/proyecto/`).

**Servidor:** `10.0.64.53` · Nginx + PHP-FPM 8.3 · Oracle Linux 8.4

---

## Sitios disponibles

| # | Proyecto | URL | Tipo | Webroot |
|---|---|---|---|---|
| — | Landing | `http://10.0.64.53/` | HTML estático | `/var/www/html/qa/` |
| 1 | corbeta_textiles_admin | `http://10.0.64.53/corbeta_textiles_admin/` | Drupal (sin `web/`) | `/var/www/vhost/corbeta_textiles_admin/` |
| 2 | corbeta_textiles | `http://10.0.64.53/corbeta_textiles/` | Angular SPA | `/var/www/vhost/corbeta_textiles/dist/textiles/` |
| 3 | agendatucita-alkomprar | `http://10.0.64.53/agendatucita-alkomprar/` | Drupal | `/var/www/vhost/agendatucita-alkomprar/web/` |
| 4 | dongfeng | `http://10.0.64.53/dongfeng/` | Drupal | `/var/www/vhost/dongfeng/web/` |
| 5 | ganaconkalley | `http://10.0.64.53/ganaconkalley/` | Drupal | `/var/www/vhost/ganaconkalley/web/` |
| 6 | invoice | `http://10.0.64.53/invoice/` | Drupal | `/var/www/vhost/invoice/web/` |
| 7 | kalleymovil | `http://10.0.64.53/kalleymovil/` | Drupal | `/var/www/vhost/kalleymovil/web/` |
| 8 | knowledgebase | `http://10.0.64.53/knowledgebase/` | Drupal | `/var/www/vhost/knowledgebase/web/` |
| 9 | landingdescargas | `http://10.0.64.53/landingdescargas/` | Drupal | `/var/www/vhost/landingdescargas/web/` |
| 10 | midia | `http://10.0.64.53/midia/` | Drupal | `/var/www/vhost/midia/web/` |
| 11 | narinenseslomaximo | `http://10.0.64.53/narinenseslomaximo/` | Drupal | `/var/www/vhost/narinenseslomaximo/web/` |
| 12 | pidetucita_alkomprar | `http://10.0.64.53/pidetucita_alkomprar/` | Drupal | `/var/www/vhost/pidetucita_alkomprar/web/` |
| 13 | redcontigo | `http://10.0.64.53/redcontigo/` | Drupal | `/var/www/vhost/redcontigo/web/` |
| 14 | servicios_kalley | `http://10.0.64.53/servicios_kalley/` | Drupal | `/var/www/vhost/servicios_kalley/web/` |
| 15 | servicios_tcl | `http://10.0.64.53/servicios_tcl/` | Drupal | `/var/www/vhost/servicios_tcl/web/` |

---

## Estructura de archivos

```
config-nginx/
├── sites-qa.conf    # Configuración única puerto 80 — todos los proyectos
├── qa-index.html    # Landing con listado de proyectos
├── qa-status.html   # Reporte visual de estado
└── qa-status.pdf    # Reporte PDF
```

---

## Arquitectura del `sites-qa.conf`

### Patrones de routing por tipo de proyecto

#### Drupal estándar (con `web/`)
Los proyectos con instalación Composer usan `web/` como webroot.
Se sirven con `root /var/www/vhost` + `try_files $uri /$project/web/index.php?$query_string`.

```nginx
location ~ ^/(?<project>dongfeng|ganaconkalley|...) {
    root /var/www/vhost;
    try_files $uri /$project/web/index.php?$query_string;

    location ~ \.php$ {
        fastcgi_param SCRIPT_FILENAME /var/www/vhost/$project/web/index.php;
        fastcgi_param SCRIPT_NAME     /$project/index.php;
        fastcgi_param DOCUMENT_ROOT   /var/www/vhost/$project/web;
    }
}
```

#### corbeta_textiles_admin (Drupal sin `web/`)
Instalación Drupal con `index.php` directamente en la raíz del proyecto.
Usa `alias` + named location para evitar el quirk de nginx donde `try_files` con
`alias` sirve archivos `.php` como estáticos en lugar de pasarlos a PHP-FPM.

```nginx
location ^~ /corbeta_textiles_admin/ {
    alias /var/www/vhost/corbeta_textiles_admin/;

    # PHP interceptado ANTES de try_files (evita descarga estática con alias)
    location ~ \.php$ {
        fastcgi_param SCRIPT_FILENAME /var/www/vhost/corbeta_textiles_admin/index.php;
        fastcgi_param SCRIPT_NAME     /corbeta_textiles_admin/index.php;
        fastcgi_param REQUEST_URI     $request_uri;
    }

    # Clean URLs y directorio raíz → named location PHP
    try_files $uri $uri/ @corbeta_textiles_admin;
}

# Named location para clean URLs (try_files fallback)
location @corbeta_textiles_admin {
    fastcgi_param SCRIPT_FILENAME /var/www/vhost/corbeta_textiles_admin/index.php;
    fastcgi_param SCRIPT_NAME     /corbeta_textiles_admin/index.php;
    fastcgi_param REQUEST_URI     $request_uri;
}
```

> **Por qué named location:** con `alias`, si `try_files` usa una URI como fallback
> (p.ej. `/corbeta_textiles_admin/index.php`), nginx hace un redirect interno y pierde
> el matching de los nested locations. La named location (`@name`) evita ese redirect
> interno y pasa directamente a PHP-FPM.

#### corbeta_textiles (Angular SPA)
```nginx
location ^~ /corbeta_textiles/ {
    alias /var/www/vhost/corbeta_textiles/dist/textiles/;
    try_files $uri $uri/ /corbeta_textiles/index.html;
    sub_filter '<base href="/">' '<base href="/corbeta_textiles/">';
}
```

---

## Drupal `settings.php`

Cada proyecto Drupal en QA requiere `trusted_host_patterns` con la IP del servidor:

```php
$settings['trusted_host_patterns'] = [
  '^10\.0\.64\.53$',
];
```

---

## Despliegue en servidor

```bash
# 1. Subir archivo
scp config-nginx/sites-qa.conf drupal@10.0.64.53:/tmp/

# 2. En el servidor (requiere terminal interactiva para sudo)
ssh -t drupal@10.0.64.53 "sudo cp /tmp/sites-qa.conf /etc/nginx/conf.d/sites/sites-qa.conf && sudo nginx -t && sudo systemctl reload nginx"
```

> El usuario `drupal` no tiene escritura directa en `/etc/nginx/conf.d/sites/`.
> El flujo correcto es: subir a `/tmp/` → copiar con `sudo` desde el servidor.
