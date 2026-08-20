# 🛠️ IT Automation Toolkit (ITAT)

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Versión de Python](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)](https://python.org)
[![Estado](https://img.shields.io/badge/estado-desarrollo--activo-orange.svg)]()
[![PRs Bienvenidos](https://img.shields.io/badge/PRs-bienvenidos-brightgreen.svg)](CONTRIBUTING.md)

**IT Automation Toolkit (ITAT)** es un framework modular, moderno y de nivel empresarial (*Enterprise-ready*) escrito en Python. Diseñado para Administradores de Sistemas TI, Ingenieros DevOps y Proveedores de Servicios Gestionados (MSPs), ITAT automatiza la auditoría de sistemas, el inventario de hardware y red, la verificación de políticas de seguridad, el envío de alertas por Webhook y el soporte automatizado de aplicaciones críticas mediante *Skills*.

---

## ✨ Características Principales

- 🎛️ **Plataforma Interactiva de Menús (`itat` o `itat menu`)**
  - Consola interactiva visual con menús numerados y soporte i18n (Español/Inglés) para navegar por todas las herramientas sin memorizar comandos.
- 🖥️ **Inventario Completo de Hardware y Red (`itat inventory`)**
  - Recolecta métricas de CPU, memoria RAM y Swap, particiones de disco físico, interfaces de red activas (IP/MAC), sesiones de usuario y procesos con mayor consumo de recursos.
  - Genera reportes ejecutivos en formatos **HTML (Dark-Mode Glassmorphism)**, **Markdown** y **JSON**, organizados automáticamente en la carpeta `/exports/`.
- 🩺 **Diagnóstico de Salud del Sistema (`itat doctor`)**
  - Evalúa la carga del procesador, presión de memoria, capacidad del disco raíz, promedio de carga y conectividad externa/DNS.
- 🛡️ **Auditoría de Seguridad y Cumplimiento (`itat audit`)**
  - Verifica el estado del sistema contra políticas de seguridad configurables (`DiskSpacePolicy`, `MemoryUsagePolicy`, `UserSecurityPolicy`).
- 🚨 **Notificaciones y Alertas vía Webhook (`--webhook <URL>`)**
  - Envío automático de alertas formateadas para **Slack**, **Discord**, **Telegram** o endpoints **REST/JSON** ante eventos de auditoría o fallos en el sistema.
- 🎫 **Gestión de Tickets e Incidentes ITSM (`itat ticket`)**
  - Base de datos SQLite integrada para registrar incidentes de clientes, notas de resolución, seguimiento de estados y exportación de reportes ejecutivos de facturación.
- ⚙️ **Abstracción de Servicios Multiplataforma (`ServiceManager`)**
  - Gestión agnóstica del sistema operativo para consultar y reiniciar servicios en **Linux** (`systemctl` con elevación segura `sudo`), **Windows** (`sc.exe` / `net`) y **macOS**.
- 🧩 **Skills Especializados de Soporte (`itat skill`)**
  - Arquitectura modular de plugins (`BaseSkill`) para diagnosticar, analizar logs y autoreparar (*auto-fix*) entornos de software específicos:
    - 🌐 **Nginx / Servidores Web (`WebServiceSkill`)**
    - 🐋 **Entorno Docker (`DockerSkill`)**: Inspección de demonio, contenedores activos y caídos (`exited`), análisis de logs y reinicio automático.
    - 🐬 **MySQL / MariaDB (`MySQLSkill`)**: Diagnóstico de socket TCP 3306, verificación del servicio y remediación.
    - 🐘 **PostgreSQL (`PostgreSQLSkill`)**: Inspección de puerto 5432, salud del servicio y análisis de logs.
    - 📊 **Power BI On-Premises Gateway (`PowerBISkill`)**: Verificación de conectividad HTTPS a la nube (`api.powerbi.com`), diagnóstico del servicio de Gateway y análisis de logs.
    - 🛡️ **Antivirus y Detección de Malware (`AntivirusSkill`)**: Inspección de procesos sospechosos corriendo en carpetas temporales (`/tmp`, `AppData/Temp`), mineros de criptomonedas, verificación de ClamAV / Windows Defender y remediación (*kill*) de procesos maliciosos.

---

## 🚀 Inicio Rápido

### 1. Instalación

Clona el repositorio e instala el Toolkit en modo editable:

```bash
git clone https://github.com/PortilloLab/it-automation-toolkit.git
cd it-automation-toolkit

# Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar dependencias y el CLI de ITAT (modo desarrollo)
pip install -e .[dev]
```

### 2. Verificar la Instalación

```bash
itat --help
itat version
```

---

## 💻 Uso de la Línea de Comandos (CLI)

### 🎛️ Menú Interactivo Visual

```bash
itat menu
```

### 🖥️ Inventario del Sistema y Exportación de Reportes

```bash
# Ver inventario completo en la terminal
itat inventory

# Exportar reportes ejecutivos a la carpeta ./exports/
itat inventory --html reporte.html --markdown reporte.md --json reporte.json
```

### 🩺 Diagnóstico de Salud (System Doctor)

```bash
# Diagnosticar estado del hardware y conectividad
itat doctor
```

### 🛡️ Auditoría de Seguridad y Alertas por Webhook

```bash
# Ejecutar auditoría y generar reporte HTML
itat audit --html auditoria.html

# Ejecutar auditoría y enviar alerta a Slack o Discord si se detectan fallos
itat audit --webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 🧩 Skills Especializados y Remedración Automática

```bash
# Listar todos los skills registrados
itat skill list

# Ejecutar diagnóstico de salud en todos los skills (Nginx, Docker, MySQL, PostgreSQL, Power BI)
itat skill health

# Analizar logs buscando patrones de error
itat skill logs --name postgresql

# Ejecutar autoreparación / reinicio de servicio (registra automáticamente un ticket en SQLite)
itat skill fix --name mysql --yes
```

### 🎫 Gestión de Tickets de Soporte

```bash
# Listar tickets abiertos
itat ticket list --status OPEN

# Crear un nuevo ticket de soporte
itat ticket create --title "Fallo de conexión en BD" --client "Cliente Alpha" --priority HIGH

# Resolver ticket indicando notas de solución
itat ticket resolve 1 --notes "Servicio restablecido mediante auto-fix de ITAT."

# Exportar reporte de tickets a HTML
itat ticket export --html reporte_tickets.html
```

---

## 🧩 Extensión de ITAT: Creación de Skills Personalizados

ITAT permite extender fácilmente la capacidad de soporte para cualquier aplicación o servicio personalizado heredando de `BaseSkill`:

```python
from itat.skills import BaseSkill, SkillResult, SkillStatus
from itat.utils.services import ServiceManager

class RedisSkill(BaseSkill):
    name = "redis"
    description = "Skill de soporte para Redis In-Memory Store"
    target_service = "redis-server"

    def check_health(self) -> SkillResult:
        is_active = ServiceManager.is_service_active(self.target_service)
        if is_active:
            return SkillResult(status=SkillStatus.OK, message="Servidor Redis en ejecución normal.")
        return SkillResult(status=SkillStatus.WARNING, message="Servicio Redis detenido.")

    def analyze_logs(self, log_path=None, lines=100) -> SkillResult:
        # Lógica personalizada de análisis de logs
        return SkillResult(status=SkillStatus.OK, message="Sin errores en los logs de Redis.")

    def auto_fix(self) -> SkillResult:
        success, msg = ServiceManager.restart_service(self.target_service)
        if success:
            return SkillResult(status=SkillStatus.OK, message=msg, actions_taken=["Servicio Redis reiniciado."])
        return SkillResult(status=SkillStatus.ERROR, message=msg)
```

Registra tu nuevo skill en `SkillManager`:

```python
from itat.skills import SkillManager

manager = SkillManager()
manager.register(RedisSkill())
```

---

## 🤝 Contribuciones

¡Las contribuciones de la comunidad son bienvenidas! Ya sea agregando nuevos skills, creando nuevas políticas de seguridad o mejorando la compatibilidad de plataformas:

1. Revisa [CONTRIBUTING.md](CONTRIBUTING.md)
2. Realiza un Fork del repositorio
3. Crea tu rama de función (`git checkout -b feature/nuevo-skill`)
4. Ejecuta las pruebas unitarias (`pytest tests/`)
5. ¡Envía un Pull Request!

---

## 📜 Licencia

Distribuido bajo la **Licencia MIT**. Consulta `LICENSE` para más información.

Desarrollado con ❤️ por **José Daniel Portillo** ([PortilloLab](https://github.com/PortilloLab)).
