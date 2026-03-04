# Ansible — instalación, configuración y ejemplos

Esta guía rápida explica cómo instalar Ansible, configurar un inventario básico y contiene ejemplos para desplegar servicios y scripts (por ejemplo `critical_report.py` y `login_report.py`) usando playbooks y templates.

**Contenido**
- Requisitos
- Instalación de Ansible
- Inventario y configuración básica
- Estructura recomendada de proyecto / roles
- Ejemplos de playbooks
- Uso de templates y handlers
- Vault y manejo de secretos
- Comandos útiles y pruebas

## Requisitos
- Control remoto por SSH en los hosts destino.
- Cuenta con privilegios sudo sin contraseña (o uso de `become` con clave interactiva si es necesario).
- Python 3 en host de control y en nodos gestionados.

## Instalación de Ansible

En Debian/Ubuntu:

```bash
sudo apt update
sudo apt install -y ansible
```

Instalación vía pip (entorno virtual recomendado):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install ansible
```

Ver versión:

```bash
ansible --version
```

## Inventario y configuración básica

Archivo `inventory` simple:

```
[servers]
server1.example.com
server2.example.com

[db]
db1.example.com
```

Archivo `ansible.cfg` mínimo en la raíz del repo:

```ini
[defaults]
inventory = ./inventory
host_key_checking = False
remote_user = ubuntu
```

## Estructura recomendada de proyecto

```
ansible-linux/
├── ansible.cfg
├── inventory
├── playbooks/
│   ├── deploy_critical_report.yml
│   └── deploy_login_report.yml
├── roles/
│   └── app/
│       ├── tasks/main.yml
│       ├── templates/mi-app.service.j2
│       └── files/critical_report.py
└── group_vars/
		└── all.yml
```

Usar `roles` facilita reutilizar tareas (crear usuario, copiar ficheros, crear venv, instalar dependencias, instalar unit files, habilitar timers).

## Ejemplo: playbook para desplegar `critical_report.py`

`playbooks/deploy_critical_report.yml` (simplificado):

```yaml
- name: Desplegar critical_report
	hosts: servers
	become: yes
	roles:
		- role: app
			vars:
				app_name: critical_report
				app_user: reporting
				app_path: /opt/curso-linux/procesos-linux
				service_template: critical_report.service.j2
```

Ejemplo de `roles/app/tasks/main.yml` (resumen):

```yaml
- name: Crear usuario
	user:
		name: "{{ app_user }}"
		system: yes

- name: Crear directorio de la app
	file:
		path: "{{ app_path }}"
		state: directory
		owner: "{{ app_user }}"

- name: Copiar scripts
	copy:
		src: critical_report.py
		dest: "{{ app_path }}/critical_report.py"
		owner: "{{ app_user }}"
		mode: '0755'

- name: Crear virtualenv
	pip:
		virtualenv: "{{ app_path }}/venv"
		requirements: "{{ app_path }}/requirements.txt"
		virtualenv_command: python3 -m venv

- name: Copiar unit file (template)
	template:
		src: "{{ service_template }}"
		dest: "/etc/systemd/system/{{ app_name }}.service"
		owner: root
		mode: '0644'

- name: systemd daemon-reload
	command: systemctl daemon-reload
	notify: restart {{ app_name }}

- name: enable timer/service
	systemd:
		name: '{{ app_name }}.timer'
		enabled: yes
		state: started

```

Handlers (roles/app/handlers/main.yml):

```yaml
- name: restart {{ app_name }}
	systemd:
		name: "{{ app_name }}.service"
		state: restarted
		daemon_reload: yes
```

## Templates y archivos

Poner `critical_report.service.j2` en `roles/app/templates/` con variables para `ExecStart`, `User`, `WorkingDirectory`, etc. Ejemplo simple:

```ini
[Unit]
Description=Reporte crítico - {{ app_name }}
After=network.target

[Service]
Type=oneshot
User={{ app_user }}
WorkingDirectory={{ app_path }}
ExecStart={{ app_path }}/venv/bin/python {{ app_path }}/critical_report.py --to "{{ recipients | default('admin@example.com') }}"

[Install]
WantedBy=timers.target
```

## Vault y manejo de secretos

Usa `ansible-vault` para cifrar credenciales (SMTP, passwords). Ejemplo:

```bash
ansible-vault create group_vars/all/vault.yml
# dentro: smtp_pass: "secreto"

# usar en playbook
- hosts: servers
	vars_files:
		- group_vars/all/vault.yml
```

Comandos útiles: `ansible-vault encrypt`, `ansible-vault decrypt`, `ansible-vault view`.

## Pruebas y despliegue

- Validar sintaxis:

```bash
ansible-playbook playbooks/deploy_critical_report.yml --check --diff
```

- Ejecutar playbook real:

```bash
ansible-playbook playbooks/deploy_critical_report.yml -K
```

(`-K` pide contraseña sudo si no está configurado `become` sin password).

## Ejemplo: tarea para crear crontab que ejecute `login_report.py`

```yaml
- name: Instalar crontab para login_report
	cron:
		name: "login_report diario"
		user: "{{ app_user }}"
		minute: 0
		hour: 1
		job: "{{ app_path }}/venv/bin/python {{ app_path }}/login_report.py --output /var/reports/login_report_$(date +\%F).pdf >> /var/log/login_report.log 2>&1"
```

## Comandos útiles

- Lint y pruebas: `ansible-lint` (instalar con pip)
- Debug remoto: `ansible -m shell -a "whoami" all`
- Ejecutar una tarea ad-hoc: `ansible servers -m copy -a "src=local dest=/tmp mode=0644"`

---

Si quieres, puedo:
- generar el esqueleto de `roles/app` con templates y tasks para `critical_report.py` y `login_report.py`,
- crear un `playbook` ya listo que copies y ejecutes contra un inventario de prueba,
- o adaptar los playbooks para usar `apt`/`yum` según tu distribución.

