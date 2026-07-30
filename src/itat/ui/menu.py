"""
Interactive Console Menu (TUI) for IT Automation Toolkit.

Provides a user-friendly, interactive menu interface so users don't need to memorize CLI flags.
Integrated with i18n translation system.
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
            print(f" [1] 🖥️  {t('menu_opt1')}")
            print(f" [2] 🩺  {t('menu_opt2')}")
            print(f" [3] 🛡️  {t('menu_opt3')}")
            print(f" [4] 🧩  {t('menu_opt4')}")
            print(f" [5] 🎫  {t('menu_opt5')}")
            print(f" [6] 📊  {t('menu_opt6')}")
            print(f" [0] 🚪  {t('menu_exit')}")
            print("=" * 65)

            choice = input(f" {t('select_option')} [0-6]: ").strip()
            print("\n")

            if choice == "1":
                self.app.execute("inventory", [])
                input(f"\n{t('press_enter')}")
            elif choice == "2":
                self.app.execute("doctor", [])
                input(f"\n{t('press_enter')}")
            elif choice == "3":
                self.app.execute("audit", [])
                input(f"\n{t('press_enter')}")
            elif choice == "4":
                self._skills_menu()
            elif choice == "5":
                self._tickets_menu()
            elif choice == "6":
                self._export_menu()
            elif choice == "0":
                print(t('exit_goodbye'))
                sys.exit(0)
            else:
                print(t('invalid_option'))

    def _print_header(self) -> None:
        print("\n" + "=" * 65)
        print(f" 🤖 IT AUTOMATION TOOLKIT (ITAT) - {t('menu_header')}")
        print("=" * 65)

    def _skills_menu(self) -> None:
        while True:
            print("\n" + "-" * 50)
            print(f" 🧩 {t('skills')}")
            print("-" * 50)
            print(f" [1] {t('skill_opt1')}")
            print(f" [2] {t('skill_opt2')}")
            print(f" [3] {t('skill_opt3')}")
            print(f" [4] {t('skill_opt4')}")
            print(f" [5] {t('skill_opt5')}")
            print(f" [0] {t('return_main')}")
            print("-" * 50)

            choice = input(f" {t('select_option')} [0-5]: ").strip()
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
                skill_name = input("Target skill (e.g. mysql, powerbi, nginx): ").strip()
                if skill_name:
                    self.app.execute("skill", ["fix", skill_name])
            elif choice == "0":
                break
            else:
                print(t('invalid_option'))
            input(f"\n{t('press_enter')}")

    def _tickets_menu(self) -> None:
        while True:
            print("\n" + "-" * 50)
            print(f" 🎫 {t('tickets')}")
            print("-" * 50)
            print(f" [1] {t('ticket_opt1')}")
            print(f" [2] {t('ticket_opt2')}")
            print(f" [3] {t('ticket_opt3')}")
            print(f" [4] {t('ticket_opt4')}")
            print(f" [0] {t('return_main')}")
            print("-" * 50)

            choice = input(f" {t('select_option')} [0-4]: ").strip()
            print("\n")
            if choice == "1":
                self.app.execute("ticket", ["list"])
            elif choice == "2":
                title = input("Title / Summary: ").strip()
                client = input("Client Name [General Client]: ").strip() or "General Client"
                priority = input("Priority (LOW/MEDIUM/HIGH/CRITICAL) [MEDIUM]: ").strip() or "MEDIUM"
                desc = input("Description: ").strip()
                if title:
                    self.app.execute("ticket", ["create", "--title", title, "--client", client, "--priority", priority, "--desc", desc])
            elif choice == "3":
                t_id = input("Ticket ID to resolve: ").strip()
                notes = input("Resolution notes: ").strip() or "Resolved by ITAT engineer"
                if t_id:
                    self.app.execute("ticket", ["resolve", t_id, "--notes", notes])
            elif choice == "4":
                file_name = input("HTML Output filename [reporte_tickets.html]: ").strip() or "reporte_tickets.html"
                self.app.execute("ticket", ["export", "--html", file_name])
            elif choice == "0":
                break
            else:
                print(t('invalid_option'))
            input(f"\n{t('press_enter')}")

    def _export_menu(self) -> None:
        print("\n" + "-" * 50)
        print(f" 📊 {t('exec_report')}")
        print("-" * 50)
        print(f" [1] {t('export_opt1')}")
        print(f" [2] {t('export_opt2')}")
        print(f" [3] {t('export_opt3')}")
        print(f" [0] {t('return_main')}")
        print("-" * 50)

        choice = input(f" {t('select_option')} [0-3]: ").strip()
        print("\n")
        if choice == "1":
            out = input("Filename [reporte_inventario.html]: ").strip() or "reporte_inventario.html"
            self.app.execute("inventory", ["--html", out])
        elif choice == "2":
            out = input("Filename [reporte_auditoria.html]: ").strip() or "reporte_auditoria.html"
            self.app.execute("audit", ["--html", out])
        elif choice == "3":
            out = input("Filename [reporte_tickets.html]: ").strip() or "reporte_tickets.html"
            self.app.execute("ticket", ["export", "--html", out])
        elif choice == "0":
            return
        input(f"\n{t('press_enter')}")
