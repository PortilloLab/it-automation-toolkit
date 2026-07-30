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
        "exec_report": "Executive Infrastructure & Incident Report",
        "system_overview": "System Overview",
        "hardware_resources": "Hardware Resources",
        "security_audit": "Security & Compliance Audit",
        "storage_partitions": "Storage Partitions",
        "network_interfaces": "Network Interfaces",
        "ticket_report_title": "ITAT Service Desk - Incident Tickets Report",
        "ticket_report_subtitle": "Consolidated customer incident and technical support log.",
        "no_tickets_found": "No tickets registered.",
        "id": "ID",
        "title_column": "Title / Incident",
        "created_at": "Created At",
        "priority": "Priority",
        "device": "Device",
        "mountpoint": "Mountpoint",
        "filesystem": "Filesystem",
        "usage": "Usage",
        "free": "Free",
        "percent": "Percent",
        "interface": "Interface",
        "ip_address": "IP Address",
        "mac_address": "MAC Address",
        "policy": "Policy",
        "severity": "Severity",
        "details": "Details",
        "menu_header": "Interactive Control Panel",
        "menu_opt1": "System Inventory (Hardware, RAM, Disks, Network)",
        "menu_opt2": "Health Diagnostics (System Doctor)",
        "menu_opt3": "Security & Compliance Audit",
        "menu_opt4": "Specialized Support Skills (MySQL, PowerBI, Web)",
        "menu_opt5": "Support Ticket Management (SQLite Helpdesk)",
        "menu_opt6": "Generate & Export Executive HTML Reports",
        "menu_exit": "Exit",
        "select_option": "Select an option",
        "press_enter": "Press Enter to continue...",
        "exit_goodbye": "Thank you for using IT Automation Toolkit (ITAT)! Goodbye!",
        "invalid_option": "Invalid option. Please try again.",
        "skill_opt1": "List all active skills",
        "skill_opt2": "Health check all services",
        "skill_opt3": "Analyze MySQL log errors",
        "skill_opt4": "Analyze Power BI log errors",
        "skill_opt5": "Execute auto-repair (Auto-Fix)",
        "return_main": "Return to main menu",
        "ticket_opt1": "List all support tickets",
        "ticket_opt2": "Create a new support ticket",
        "ticket_opt3": "Mark ticket as resolved",
        "ticket_opt4": "Export tickets report to HTML",
        "export_opt1": "Export System Inventory to HTML",
        "export_opt2": "Export Security Audit to HTML",
        "export_opt3": "Export Support Tickets Summary to HTML",
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
        "exec_report": "Informe Ejecutivo de Infraestructura e Incidencias",
        "system_overview": "Resumen del Sistema",
        "hardware_resources": "Recursos de Hardware",
        "security_audit": "Auditoría de Seguridad y Cumplimiento",
        "storage_partitions": "Particiones de Almacenamiento",
        "network_interfaces": "Interfaces de Red",
        "ticket_report_title": "ITAT Service Desk - Informe de Tickets",
        "ticket_report_subtitle": "Reporte consolidado de incidencias y soporte técnico a clientes.",
        "no_tickets_found": "Sin tickets registrados.",
        "id": "ID",
        "title_column": "Título / Incidencia",
        "created_at": "Fecha de Creación",
        "priority": "Prioridad",
        "device": "Dispositivo",
        "mountpoint": "Punto de Montaje",
        "filesystem": "Sistema de Archivos",
        "usage": "Uso",
        "free": "Libre",
        "percent": "Porcentaje",
        "interface": "Interfaz",
        "ip_address": "Dirección IP",
        "mac_address": "Dirección MAC",
        "policy": "Política",
        "severity": "Severidad",
        "details": "Detalles",
        "menu_header": "Panel de Control Interactivo",
        "menu_opt1": "Inventario del Sistema (Hardware, RAM, Discos, Red)",
        "menu_opt2": "Diagnóstico de Salud (System Doctor)",
        "menu_opt3": "Auditoría de Seguridad y Cumplimiento",
        "menu_opt4": "Skills de Soporte Especializado (MySQL, PowerBI, Web)",
        "menu_opt5": "Gestión de Tickets de Soporte (Helpdesk SQLite)",
        "menu_opt6": "Generar y Exportar Reportes Ejecutivos HTML",
        "menu_exit": "Salir",
        "select_option": "Seleccione una opción",
        "press_enter": "Presione Enter para continuar...",
        "exit_goodbye": "¡Gracias por utilizar IT Automation Toolkit (ITAT)! ¡Hasta pronto!",
        "invalid_option": "Opción no válida. Intente de nuevo.",
        "skill_opt1": "Listar todos los skills activos",
        "skill_opt2": "Diagnosticar salud de todos los servicios",
        "skill_opt3": "Analizar logs de errores de MySQL",
        "skill_opt4": "Analizar logs de errores de Power BI",
        "skill_opt5": "Ejecutar reparación automática (Auto-Fix)",
        "return_main": "Volver al menú principal",
        "ticket_opt1": "Listar todos los tickets",
        "ticket_opt2": "Crear un nuevo ticket de soporte",
        "ticket_opt3": "Marcar ticket como resuelto",
        "ticket_opt4": "Exportar reporte de tickets a HTML",
        "export_opt1": "Exportar Inventario del Sistema en HTML",
        "export_opt2": "Exportar Auditoría de Seguridad en HTML",
        "export_opt3": "Exportar Resumen de Tickets de Soporte en HTML",
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
