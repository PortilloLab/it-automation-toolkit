# 🛠️ IT Automation Toolkit (ITAT)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-brightgreen.svg)](https://python.org)
[![Status](https://img.shields.io/badge/status-active--development-orange.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**IT Automation Toolkit (ITAT)** is a modern, modular, enterprise-ready Python framework designed for IT System Administrators, DevOps Engineers, and Managed Service Providers (MSPs). It automates system auditing, hardware/network inventory scanning, security compliance checks, and specialized client software support ("Skills").

---

## ✨ Key Features

- 🎛️ **Plataforma Interactiva de Menús (`itat` o `itat menu`)**
  - Consola interactiva visual con menús numerados para navegar por todas las herramientas sin memorizar comandos.
- 🖥️ **Full Hardware & Network Inventory (`itat inventory`)**
  - Collects CPU, RAM & Swap memory, physical disk partitions, active network interfaces (IP/MAC), active user sessions, and top resource-consuming processes.
  - Generates executive reports in **Dark-Mode Glassmorphism HTML**, **Markdown**, and **JSON**.
- 🩺 **System Doctor & Health Check (`itat doctor`)**
  - Diagnoses CPU load, memory pressure, root disk capacity, load averages, and outbound internet/DNS connectivity.
- 🛡️ **Security Policy & Compliance Audit (`itat audit`)**
  - Evaluates system state against configurable security policies (`DiskSpacePolicy`, `MemoryUsagePolicy`, `UserSecurityPolicy`).
- 🎫 **Service Desk & Ticket Management (`itat ticket`)**
  - Local SQLite database to record client incidents, resolution notes, and export monthly executive billing reports.
- 🔌 **Remote Connectors & Automation SDK (`src/itat/connectors/`)**
  - Modular Python classes (`HTTPConnector` & `SSHConnector`) to transmit telemetry, trigger REST API webhooks, or perform secure SSH administration.
- 🧩 **Specialized Client Support Skills (`itat skill`)**
  - Modular plugin architecture (`BaseSkill`) to diagnose, analyze logs, and auto-repair specific software stacks:
    - **Nginx / Web Services (`WebServiceSkill`)**
    - **Docker Daemon Service (systemd integration via `WebServiceSkill`)**
    - **MySQL / MariaDB (`MySQLSkill`)**
    - **Power BI On-Premises Data Gateway & Cloud Connectivity (`PowerBISkill`)**

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/PortilloLab/it-automation-toolkit.git
cd it-automation-toolkit

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and ITAT CLI (development mode)
pip install -e .[dev]
```

### 2. Verify Installation

```bash
itat --help
itat version
```

---

## 💻 CLI Usage

### System Inventory & Reporting

```bash
# View complete inventory in terminal
itat inventory

# Export executive reports to HTML, Markdown, and JSON
itat inventory --html report.html --markdown report.md --json report.json
```

### Health Diagnostics

```bash
# Run system health checks
itat doctor
```

### Security & Compliance Audit

```bash
# Execute policy checks and export executive audit report
itat audit --html audit_report.html
```

### Specialized Client Support Skills

```bash
# List all registered skills
itat skill list

# Run health diagnostics across client skills (Nginx, MySQL, Power BI, Docker)
itat skill health

# Analyze application log files for error patterns
itat skill logs --name mysql

# Execute automated remediation / service restart (includes safety confirmation prompt)
itat skill fix --name mysql --yes
```

---

## 🧩 Extending ITAT: Writing Custom Skills

ITAT is designed to be easily extended with custom support skills for your clients' specific software stacks.

Simply inherit from `BaseSkill`:

```python
from itat.skills import BaseSkill, SkillResult, SkillStatus

class RedisSkill(BaseSkill):
    name = "redis"
    description = "Support skill for Redis In-Memory Store"
    target_service = "redis-server"

    def check_health(self) -> SkillResult:
        # Custom health logic here
        return SkillResult(status=SkillStatus.OK, message="Redis server is running smoothly.")

    def analyze_logs(self, log_path=None, lines=100) -> SkillResult:
        # Custom log analysis logic
        return SkillResult(status=SkillStatus.OK, message="No errors in Redis logs.")

    def auto_fix(self) -> SkillResult:
        # Custom remediation logic
        return SkillResult(status=SkillStatus.OK, message="Restarted Redis service.", actions_taken=["systemctl restart redis"])
```

Register your skill in `SkillManager`:

```python
from itat.skills import SkillManager

manager = SkillManager()
manager.register(RedisSkill())
```

---

## 🤝 Contributing

Contributions from the open-source community are welcome! Whether it's adding new skills, refining policy engines, or expanding OS compatibility:

1. Review [CONTRIBUTING.md](CONTRIBUTING.md)
2. Fork the repository
3. Create a feature branch (`git checkout -b feature/awesome-skill`)
4. Run unit tests (`pytest tests/`)
5. Submit a Pull Request!

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for more information.

Developed with ❤️ by **José Daniel Portillo** ([PortilloLab](https://github.com/PortilloLab)).
