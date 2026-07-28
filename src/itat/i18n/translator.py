"""
Internationalization (i18n) module for IT Automation Toolkit.

Supports English (en) and Spanish (es).
"""

from typing import Dict, Any

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "title": "IT Automation Toolkit",
        "inventory": "System Inventory",
        "doctor": "System Health Diagnostics",
        "audit": "Compliance & Security Audit",
        "tickets": "Ticket Management",
        "skills": "Specialized Support Skills",
        "system": "SYSTEM",
        "cpu": "CPU",
        "memory": "RAM & SWAP MEMORY",
        "disks": "STORAGE & DISKS",
        "network": "NETWORK INTERFACES",
        "processes": "TOP RESOURCE PROCESSES",
        "status": "Status",
        "passed": "Passed",
        "warnings": "Warnings",
        "failures": "Failures",
        "client": "Client",
        "ticket_created": "Ticket created successfully",
        "ticket_resolved": "Ticket resolved successfully",
    },
    "es": {
        "title": "IT Automation Toolkit",
        "inventory": "Inventario del Sistema",
        "doctor": "Diagnóstico de Salud del Sistema",
        "audit": "Auditoría de Seguridad y Cumplimiento",
        "tickets": "Gestión de Tickets de Soporte",
        "skills": "Skills de Soporte Especializado",
        "system": "SISTEMA",
        "cpu": "PROCESADOR (CPU)",
        "memory": "MEMORIA RAM Y SWAP",
        "disks": "ALMACENAMIENTO Y DISCOS",
        "network": "INTERFACES DE RED",
        "processes": "PROCESOS DE MAYOR CONSUMO",
        "status": "Estado",
        "passed": "Pasados",
        "warnings": "Advertencias",
        "failures": "Fallos",
        "client": "Cliente",
        "ticket_created": "Ticket creado exitosamente",
        "ticket_resolved": "Ticket resuelto exitosamente",
    },
}

DEFAULT_LANG = "es"


class Translator:
    """Translation manager."""

    def __init__(self, lang: str = DEFAULT_LANG):
        self.lang = lang if lang in TRANSLATIONS else DEFAULT_LANG

    def set_language(self, lang: str) -> None:
        if lang in TRANSLATIONS:
            self.lang = lang

    def get(self, key: str, default: str = "") -> str:
        """Get translated string for key."""
        return TRANSLATIONS.get(self.lang, {}).get(key, default or key)

    def __call__(self, key: str, default: str = "") -> str:
        return self.get(key, default)


# Global instance
t = Translator(DEFAULT_LANG)
