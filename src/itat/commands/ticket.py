"""
Ticket Command for managing IT service tickets and ITSM records.
"""

import html
from typing import List, Optional
from itat.core.command import Command
from itat.tickets import TicketDatabase
from itat.i18n import t
from itat.utils.paths import ensure_export_path


class TicketCommand(Command):
    """
    Ticket command for IT service desk ticket management.
    """

    name = "ticket"
    description = "Manage IT service desk tickets and incident records."

    def __init__(self):
        super().__init__()
        self.db = TicketDatabase()

    def run(self, args: Optional[List[str]] = None) -> int:
        args = args or []
        subcommand = args[0] if args else "list"

        if subcommand in ("list", "--list"):
            status = self._get_arg_value(args, "--status") or self._get_arg_value(args, "-s")
            client = self._get_arg_value(args, "--client") or self._get_arg_value(args, "-c")
            return self._handle_list(status, client)

        elif subcommand in ("create", "add", "new"):
            title = self._get_arg_value(args, "--title") or self._get_arg_value(args, "-t")
            if not title and len(args) > 1 and not args[1].startswith("-"):
                title = args[1]
            if not title:
                print("Error: Missing ticket title. Usage: itat ticket create --title 'Issue summary'")
                return 1
            client = self._get_arg_value(args, "--client") or "General Client"
            priority = self._get_arg_value(args, "--priority") or "MEDIUM"
            desc = self._get_arg_value(args, "--desc") or ""
            skill = self._get_arg_value(args, "--skill") or ""
            return self._handle_create(title, desc, client, priority, skill)

        elif subcommand in ("show", "get"):
            if len(args) < 2 or not args[1].isdigit():
                print("Error: Specify a valid ticket ID. Usage: itat ticket show <ticket_id>")
                return 1
            return self._handle_show(int(args[1]))

        elif subcommand in ("resolve", "close", "fix"):
            if len(args) < 2 or not args[1].isdigit():
                print("Error: Specify a valid ticket ID. Usage: itat ticket resolve <ticket_id> [--notes '...']")
                return 1
            notes = self._get_arg_value(args, "--notes") or "Resolved by ITAT engineer."
            return self._handle_resolve(int(args[1]), notes)

        elif subcommand in ("export", "report"):
            html_file = self._get_arg_value(args, "--html") or "ticket_report.html"
            return self._handle_export_html(html_file)

        else:
            print(f"Unknown ticket subcommand: '{subcommand}'")
            print("Usage: itat ticket [list | create | show | resolve | export]")
            return 1

    def _handle_create(self, title: str, desc: str, client: str, priority: str, skill: str) -> int:
        ticket_id = self.db.create_ticket(
            title=title,
            description=desc,
            client_name=client,
            priority=priority,
            skill_name=skill,
        )
        print("=" * 60)
        print(f"✔ {t('ticket_created')} [ID #{ticket_id}]")
        print(f"  Title       : {title}")
        print(f"  Client      : {client}")
        print(f"  Priority    : {priority.upper()}")
        print("=" * 60)
        return 0

    def _handle_list(self, status: Optional[str], client: Optional[str]) -> int:
        tickets = self.db.list_tickets(status=status, client_name=client)
        print("=" * 60)
        print("ITAT Service Desk - Incident & Support Tickets")
        print("=" * 60)
        if not tickets:
            print("No tickets found matching criteria.")
            return 0

        for tk in tickets:
            status_badge = f"[{tk['status']}]"
            print(f"• Ticket #{tk['id']:<3} {status_badge:<12} Priority: {tk['priority']:<8} Client: {tk['client_name']}")
            print(f"  Title      : {tk['title']}")
            print(f"  Created At : {tk['created_at']}")
            if tk['status'] == 'RESOLVED':
                print(f"  Resolved At: {tk['resolved_at']}")
                print(f"  Notes      : {tk['resolution_notes']}")
            print("-" * 60)
        return 0

    def _handle_show(self, ticket_id: int) -> int:
        tk = self.db.get_ticket(ticket_id)
        if not tk:
            print(f"Ticket #{ticket_id} not found.")
            return 1
        print("=" * 60)
        print(f"Ticket #{tk['id']} Details")
        print("=" * 60)
        print(f"Title       : {tk['title']}")
        print(f"Status      : {tk['status']}")
        print(f"Client      : {tk['client_name']}")
        print(f"Priority    : {tk['priority']}")
        print(f"Created At  : {tk['created_at']}")
        if tk['description']:
            print(f"Description : {tk['description']}")
        if tk['status'] == 'RESOLVED':
            print(f"Resolved At : {tk['resolved_at']}")
            print(f"Notes       : {tk['resolution_notes']}")
        print("=" * 60)
        return 0

    def _handle_resolve(self, ticket_id: int, notes: str) -> int:
        success = self.db.resolve_ticket(ticket_id, notes)
        if success:
            print(f"✔ Ticket #{ticket_id} resolved successfully.")
            return 0
        else:
            print(f"Failed to resolve ticket #{ticket_id}. Verification failed.")
            return 1

    def _handle_export_html(self, html_file: str) -> int:
        html_file = ensure_export_path(html_file, "reporte_tickets.html")
        tickets = self.db.list_tickets()
        rows_html = ""
        for tk in tickets:
            status_cls = "status-open" if tk['status'] == 'OPEN' else "status-resolved"
            client_esc = html.escape(str(tk['client_name']))
            title_esc = html.escape(str(tk['title']))
            status_esc = html.escape(str(tk['status']))
            priority_esc = html.escape(str(tk['priority']))
            created_esc = html.escape(str(tk['created_at']))
            rows_html += f"""
            <tr>
                <td>#{tk['id']}</td>
                <td>{client_esc}</td>
                <td>{title_esc}</td>
                <td><span class="badge {status_cls}">{status_esc}</span></td>
                <td>{priority_esc}</td>
                <td>{created_esc}</td>
            </tr>
            """

        empty_msg = html.escape(t('no_tickets_found'))
        html_content = f"""<!DOCTYPE html>
<html lang="{t.lang}">
<head>
    <meta charset="UTF-8">
    <title>{t('ticket_report_title')}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 30px; }}
        .card {{ background: #1e293b; border-radius: 12px; padding: 24px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }}
        h1 {{ color: #38bdf8; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background-color: #0f172a; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }}
        .badge {{ padding: 4px 10px; border-radius: 9999px; font-weight: bold; font-size: 0.75rem; }}
        .status-open {{ background: #ef4444; color: #fff; }}
        .status-resolved {{ background: #22c55e; color: #fff; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>🎫 {t('ticket_report_title')}</h1>
        <p>{t('ticket_report_subtitle')}</p>
        <table>
            <thead>
                <tr>
                    <th>{t('id')}</th>
                    <th>{t('client')}</th>
                    <th>{t('title_column')}</th>
                    <th>{t('status')}</th>
                    <th>{t('priority')}</th>
                    <th>{t('created_at')}</th>
                </tr>
            </thead>
            <tbody>
                {rows_html if rows_html else f"<tr><td colspan='6'>{empty_msg}</td></tr>"}
            </tbody>
        </table>
    </div>
</body>
</html>"""
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"✔ Executive Ticket HTML Report generated at: {html_file}")
        return 0
