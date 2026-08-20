"""
Audit command for running system compliance policies.
"""

from itat.core.command import Command
from itat.inventory.scanner import scan
from itat.policies import PolicyEngine
from itat.inventory.export import export_json, export_markdown
from itat.reports import generate_html_report
from itat.connectors.http import HTTPConnector
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

        # Handle Webhook Notification
        if "--webhook" in args:
            idx = args.index("--webhook")
            if idx + 1 < len(args):
                webhook_url = args[idx + 1]
                conn = HTTPConnector(webhook_url)
                severity_level = "CRITICAL" if failures > 0 else ("WARNING" if warnings > 0 else "INFO")
                alert_text = f"Host: {inventory['system'].hostname}\nSummary: {summary_msg}"
                if failures > 0 or warnings > 0:
                    violations = [f"• {r.policy_name}: {r.message}" for r in results if not r.passed]
                    alert_text += "\n\nViolations:\n" + "\n".join(violations)

                if conn.send_alert("ITAT Security & Audit Alert", alert_text, severity=severity_level):
                    print(f"\n[+] Webhook alert sent successfully to: {webhook_url}")
                else:
                    print(f"\n[!] Failed sending webhook alert to: {webhook_url}")

        # Handle exports
        if "--html" in args:
            idx = args.index("--html")
            if idx + 1 < len(args):
                out = args[idx + 1]
                saved_out = generate_html_report(inventory, results, out)
                print(f"\n[+] HTML Executive Report generated: {saved_out}")

        if "--markdown" in args or "-m" in args:
            flag = "--markdown" if "--markdown" in args else "-m"
            idx = args.index(flag)
            if idx + 1 < len(args):
                out = args[idx + 1]
                saved_out = export_markdown(inventory, out)
                print(f"[+] Audit Markdown exported: {saved_out}")

        if "--json" in args:
            idx = args.index("--json")
            if idx + 1 < len(args):
                out = args[idx + 1]
                saved_out = export_json(inventory, out)
                print(f"[+] Audit JSON exported: {saved_out}")

        return 0 if failures == 0 else 1
