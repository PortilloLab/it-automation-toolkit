# 📖 Manual de Usuario - IT Automation Toolkit (ITAT)

Bienvenido al **Manual de Usuario oficial de ITAT**. Esta guía contiene todas las instrucciones detalladas para instalar, utilizar y extender el kit de automatización de TI.

---

## 📋 Índice
1. [Instalación y Configuración Inicial](#1-instalación-y-configuración-inicial)
2. [Soporte Multilingüe (i18n)](#2-soporte-multilingüe-i18n)
3. [Comandos de la CLI](#3-comandos-de-la-cli)
   - [`itat inventory`](#itat-inventory)
   - [`itat doctor`](#itat-doctor)
   - [`itat audit`](#itat-audit)
   - [`itat skill`](#itat-skill)
   - [`itat ticket`](#itat-ticket)
4. [Gestión de Tickets de Soporte (ITSM)](#4-gestión-de-tickets-de-soporte-itsm)
5. [Generación de Reportes Ejecutivos](#5-generación-de-reportes-ejecutivos)

---

## 1. Instalación y Configuración Inicial

### Requisitos previos:
- Python 3.11 o superior.
- Git.

### Pasos de instalación:
```bash
git clone https://github.com/PortilloLab/it-automation-toolkit.git
cd it-automation-toolkit

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar CLI en modo desarrollo
pip install -e .
```

---

## 2. Soporte Multilingüe (i18n)

ITAT admite **Español (`es`)** e **Inglés (`en`)** para adaptar los textos de salida en terminal y reportes.

Por defecto, ITAT opera en español. Para especificar el idioma o consultar traducciones:
```bash
itat --help
```

---

## 3. Comandos de la CLI

### `itat inventory`
Recolecta el inventario completo de hardware, sistema operativo, almacenamiento, interfaces de red y procesos principales.

```bash
# Salida en pantalla
itat inventory

# Exportar a PDF corporativo, HTML, Markdown y JSON
itat inventory --pdf inventario.pdf --html reporte.html --markdown reporte.md --json reporte.json
```

---

### `itat doctor`
Realiza un chequeo de salud y diagnóstico rápido del hardware, uso de CPU, RAM, espacio libre en disco `/` y conectividad a Internet.

```bash
itat doctor
```

---

### `itat audit`
Audita la infraestructura evaluando políticas de seguridad (espacio mínimo en disco, límites de memoria RAM, swap y ejecución en modo usuario estándar), con soporte para generación de informes PDF ejecutivos, perfiles multi-cliente y canales de alerta.

```bash
# Auditoría con reporte HTML o PDF ejecutivo
itat audit --html auditoria_cliente.html
itat audit --pdf auditoria_ejecutiva.pdf

# Auditoría con perfil personalizado de cliente
itat audit --config configs/client_enterprise.json

# Despachar alertas a Webhook (Slack/Discord), Telegram y Correo SMTP (adjuntando PDF)
itat audit --pdf auditoria.pdf --email soc@empresa.com
itat audit --webhook https://hooks.slack.com/services/...
itat audit --telegram "BOT_TOKEN:CHAT_ID"

# Ejecutar con perfil pero sin emitir alertas
itat audit --config configs/client_enterprise.json --no-alerts
```

---

### `itat skill`
Gestión y ejecución de **Skills de Soporte Especializado** para servicios como Nginx, Docker, MySQL, PostgreSQL, Power BI On-Premises Gateway, Antivirus, Certificados SSL/TLS y Actualizaciones del Sistema Operativo.

```bash
# Listar todos los skills disponibles
itat skill list

# Ejecutar diagnóstico de salud de los servicios cliente
itat skill health

# Analizar logs de errores en busca de palabras clave críticas
itat skill logs --name mysql

# Ejecutar reparación automática / reinicio del servicio
itat skill fix mysql
```

---

## 4. Gestión de Tickets de Soporte (ITSM)

El módulo **`itat ticket`** almacena incidencias en una base de datos ligera **SQLite** guardada localmente en `~/.itat/tickets.db`.

```bash
# Crear un nuevo ticket de soporte
itat ticket create --title "Fallo de conexión en base de datos" --client "Cliente Acme" --priority HIGH

# Listar tickets registrados
itat ticket list

# Ver detalle de un ticket específico
itat ticket show 1

# Resolver un ticket con notas de trabajo
itat ticket resolve 1 --notes "Se reinició servicio MySQL y se limpió espacio en disco"

# Exportar informe ejecutivo de tickets a HTML para cobro/cliente
itat ticket export --html reporte_tickets.html
```

---

## 5. Generación de Reportes Ejecutivos

Los informes en **HTML (Dark Mode Glassmorphism)** están diseñados para enviarse a clientes o directores de tecnología, mostrando un diseño limpio y moderno con métricas clave.

```bash
itat inventory --html reporte_ejecutivo.html
itat audit --html auditoria_cumplimiento.html
itat ticket export --html estado_incidencias.html
```
