"""
Audit command for running system compliance policies.
"""

from itat.core.command import Command
from itat.inventory.scanner import scan
from itat.policies import PolicyEngine
from itat.inventory.export import export_json, export_markdown
from itat.reports import generate_html_report
from itat.connectors import HTTPConnector, TelegramConnector, EmailConnector
from itat.i18n import t


class AuditCommand(Command):
    """
    Audit command executes policy suite against current inventory.
    """

    name = "audit"
    description = "Audit system compliance against security policies."

    def run(self, args: list[str]) -> int:
        print("=" * 60)
        print(f"IT Automation Toolkit - {t('audit')}")
        print("=" * 60)

        inventory = scan()
        engine = PolicyEngine()
        results = engine.evaluate_all(inventory)

        failures = 0
        warnings = 0

        print(f"\n{t('security_audit').upper()}")
        print("-" * 60)
        for res in results:
            if res.passed:
                badge = "[ PASSED ]"
            else:
                badge = "[ FAILED ]"
                if res.severity in ("HIGH", "CRITICAL"):
                    failures += 1
                else:
                    warnings += 1

            print(f"{badge:<11} [{res.severity:<8}] {res.policy_name}")
            print(f"            {t('details')}: {res.message}")

        print("-" * 60)
        summary_msg = f"{len(results) - failures - warnings} {t('passed')} | {warnings} {t('warnings')} | {failures} {t('failures')}"
        print(f"Audit Summary: {summary_msg}")

        severity_level = "CRITICAL" if failures > 0 else ("WARNING" if warnings > 0 else "INFO")
        alert_text = f"Host: {inventory['system'].hostname}\nSummary: {summary_msg}"
        if failures > 0 or warnings > 0:
            violations = [f"• {r.policy_name}: {r.message}" for r in results if not r.passed]
            alert_text += "\n\nViolations:\n" + "\n".join(violations)

        # Handle Webhook Notification (Slack/Discord)
        webhook_url = self._get_arg_value(args, "--webhook")
        if webhook_url:
            conn = HTTPConnector(webhook_url)
            if conn.send_alert("ITAT Security & Audit Alert", alert_text, severity=severity_level):
                print(f"\n[+] Webhook alert sent successfully to: {webhook_url}")
            else:
                print(f"\n[!] Failed sending webhook alert to: {webhook_url}")

        # Handle Telegram Notification
        if "--telegram" in args:
            tg_arg = self._get_arg_value(args, "--telegram")
            bot_token, chat_id = None, None
            if tg_arg and ":" in tg_arg:
                parts = tg_arg.split(":", 1)
                bot_token, chat_id = parts[0], parts[1]

            tg_conn = TelegramConnector(bot_token=bot_token, chat_id=chat_id)
            if tg_conn.send_alert("ITAT Security & Audit Alert", alert_text, severity=severity_level):
                print(f"\n[+] Telegram alert sent successfully (Chat ID: {tg_conn.chat_id})")
            else:
                print("\n[!] Failed sending Telegram alert. Check bot token and chat ID.")

        # Handle exports first (so email can attach HTML if generated)
        saved_html = None
        html_out = self._get_arg_value(args, "--html")
        if html_out:
            saved_html = generate_html_report(inventory, results, html_out)
            print(f"\n[+] HTML Executive Report generated: {saved_html}")

        md_out = self._get_arg_value(args, "--markdown") or self._get_arg_value(args, "-m")
        if md_out:
            saved_md = export_markdown(inventory, md_out)
            print(f"[+] Audit Markdown exported: {saved_md}")

        json_out = self._get_arg_value(args, "--json")
        if json_out:
            saved_json = export_json(inventory, json_out)
            print(f"[+] Audit JSON exported: {saved_json}")

        # Handle Email Notification
        recipient = self._get_arg_value(args, "--email")
        if recipient or "--email" in args:
            email_conn = EmailConnector(default_recipient=recipient)
            if email_conn.send_alert(
                title="ITAT Security & Audit Alert",
                text=alert_text,
                severity=severity_level,
                attachment_path=saved_html,
            ):
                print(f"\n[+] Email alert sent successfully to: {recipient or email_conn.default_recipient}")
            else:
                print(f"\n[!] Failed sending email alert to: {recipient or email_conn.default_recipient}")

        return 0 if failures == 0 else 1
