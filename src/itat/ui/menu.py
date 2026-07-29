"""
Interactive Console Menu (TUI) for IT Automation Toolkit.

Provides a user-friendly, interactive menu interface so users don't need to memorize CLI flags.
"""

import sys
from typing import Optional
from itat.core.application import Application
from itat.i18n import t


class InteractiveMenu:
    """
    Interactive Console Menu system for ITAT.
    """

    def __init__(self, app: Application):
        self.app = app

    def start(self) -> None:
        """Launch the main interactive menu loop."""
        while True:
            self._print_header()
            print(" [1] 🖥️  Inventario del Sistema (Hardware, RAM, Discos, Red)")
            print(" [2] 🩺  Diagnóstico de Salud (System Doctor)")
            print(" [3] 🛡️  Auditoría de Seguridad y Cumplimiento")
            print(" [4] 🧩  Skills de Soporte Especializado (MySQL, PowerBI, Web)")
            print(" [5] 🎫  Gestión de Tickets de Soporte (Helpdesk SQLite)")
            print(" [6] 📊  Generar y Exportar Reportes Ejecutivos HTML")
            print(" [0] 🚪  Salir")
            print("=" * 65)

            choice = input(" Seleccione una opción [0-6]: ").strip()
            print("\n")

            if choice == "1":
                self.app.execute("inventory", [])
                input("\nPresione Enter para continuar...")
            elif choice == "2":
                self.app.execute("doctor", [])
                input("\nPresione Enter para continuar...")
            elif choice == "3":
                self.app.execute("audit", [])
                input("\nPresione Enter para continuar...")
            elif choice == "4":
                self._skills_menu()
            elif choice == "5":
                self._tickets_menu()
            elif choice == "6":
                self._export_menu()
            elif choice == "0":
                print("¡Gracias por utilizar IT Automation Toolkit (ITAT)! ¡Hasta pronto!")
                sys.exit(0)
            else:
                print("Opción no válida. Intente de nuevo.")

    def _print_header(self) -> None:
        print("\n" + "=" * 65)
        print(" 🤖 IT AUTOMATION TOOLKIT (ITAT) - Panel de Control Interactivo")
        print("=" * 65)

    def _skills_menu(self) -> None:
        while True:
            print("\n" + "-" * 50)
            print(" 🧩 Menú de Skills de Soporte Especializado")
            print("-" * 50)
            print(" [1] Listar todos los Skills activos")
            print(" [2] Diagnosticar salud de todos los servicios")
            print(" [3] Analizar logs de errores de MySQL")
            print(" [4] Analizar logs de errores de Power BI")
            print(" [5] Ejecutar reparación automática (Auto-Fix)")
            print(" [0] Volver al menú principal")
            print("-" * 50)

            choice = input(" Seleccione opción [0-5]: ").strip()
            print("\n")
            if choice == "1":
                self.app.execute("skill", ["list"])
            elif choice == "2":
                self.app.execute("skill", ["health"])
            elif choice == "3":
                self.app.execute("skill", ["logs", "--name", "mysql"])
            elif choice == "4":
                self.app.execute("skill", ["logs", "--name", "powerbi"])
            elif choice == "5":
                skill_name = input("Ingrese el nombre del skill a reparar (ej: mysql, powerbi, nginx): ").strip()
                if skill_name:
                    self.app.execute("skill", ["fix", skill_name])
            elif choice == "0":
                break
            else:
                print("Opción no válida.")
            input("\nPresione Enter para continuar...")

    def _tickets_menu(self) -> None:
        while True:
            print("\n" + "-" * 50)
            print(" 🎫 Menú de Gestión de Tickets (Helpdesk)")
            print("-" * 50)
            print(" [1] Listar todos los tickets")
            print(" [2] Crear un nuevo ticket de soporte")
            print(" [3] Marcar ticket como resuelto")
            print(" [4] Exportar reporte de tickets a HTML")
            print(" [0] Volver al menú principal")
            print("-" * 50)

            choice = input(" Seleccione opción [0-4]: ").strip()
            print("\n")
            if choice == "1":
                self.app.execute("ticket", ["list"])
            elif choice == "2":
                title = input("Título / Resumen de la incidencia: ").strip()
                client = input("Nombre del Cliente (opcional): ").strip() or "General Client"
                priority = input("Prioridad (LOW/MEDIUM/HIGH/CRITICAL) [MEDIUM]: ").strip() or "MEDIUM"
                desc = input("Descripción detallada (opcional): ").strip()
                if title:
                    self.app.execute("ticket", ["create", "--title", title, "--client", client, "--priority", priority, "--desc", desc])
            elif choice == "3":
                t_id = input("Ingrese el ID del ticket a resolver: ").strip()
                notes = input("Notas de la solución realizada: ").strip() or "Resuelto por ingeniero de soporte ITAT"
                if t_id:
                    self.app.execute("ticket", ["resolve", t_id, "--notes", notes])
            elif choice == "4":
                file_name = input("Nombre del archivo HTML output [reporte_tickets.html]: ").strip() or "reporte_tickets.html"
                self.app.execute("ticket", ["export", "--html", file_name])
            elif choice == "0":
                break
            else:
                print("Opción no válida.")
            input("\nPresione Enter para continuar...")

    def _export_menu(self) -> None:
        print("\n" + "-" * 50)
        print(" 📊 Generar y Exportar Reportes Ejecutivos")
        print("-" * 50)
        print(" [1] Exportar Inventario del Sistema en HTML")
        print(" [2] Exportar Auditoría de Seguridad en HTML")
        print(" [3] Exportar Resumen de Tickets de Soporte en HTML")
        print(" [0] Volver al menú principal")
        print("-" * 50)

        choice = input(" Seleccione opción [0-3]: ").strip()
        print("\n")
        if choice == "1":
            out = input("Nombre del archivo [reporte_inventario.html]: ").strip() or "reporte_inventario.html"
            self.app.execute("inventory", ["--html", out])
        elif choice == "2":
            out = input("Nombre del archivo [reporte_auditoria.html]: ").strip() or "reporte_auditoria.html"
            self.app.execute("audit", ["--html", out])
        elif choice == "3":
            out = input("Nombre del archivo [reporte_tickets.html]: ").strip() or "reporte_tickets.html"
            self.app.execute("ticket", ["export", "--html", out])
        elif choice == "0":
            return
        input("\nPresione Enter para continuar...")
