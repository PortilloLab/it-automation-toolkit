"""
Audit command for running system compliance policies.
"""

from itat.core.command import Command
from itat.inventory.scanner import scan
from itat.policies import PolicyEngine
from itat.inventory.export import export_json, export_markdown
from itat.reports import generate_html_report


class AuditCommand(Command):
    """
    Audit command executes policy suite against current inventory.
    """

    name = "audit"
    description = "Audit system compliance against security policies."

    def run(self, args: list[str]) -> int:
        print("=" * 60)
        print("IT Automation Toolkit - System Audit & Compliance")
        print("=" * 60)

        inventory = scan()
        engine = PolicyEngine()
        results = engine.evaluate_all(inventory)

        failures = 0
        warnings = 0

        print("\nPOLICY EVALUATION")
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
            print(f"            Details: {res.message}")

        print("-" * 60)
        print(f"Audit Summary: {len(results) - failures - warnings} Passed | {warnings} Warnings | {failures} Failures")

        # Handle exports
        if "--html" in args:
            idx = args.index("--html")
            if idx + 1 < len(args):
                out = args[idx + 1]
                generate_html_report(inventory, results, out)
                print(f"\n[+] HTML Executive Report generated: {out}")

        if "--markdown" in args or "-m" in args:
            flag = "--markdown" if "--markdown" in args else "-m"
            idx = args.index(flag)
            if idx + 1 < len(args):
                out = args[idx + 1]
                export_markdown(inventory, out)
                print(f"[+] Audit Markdown exported: {out}")

        if "--json" in args:
            idx = args.index("--json")
            if idx + 1 < len(args):
                out = args[idx + 1]
                export_json(inventory, out)
                print(f"[+] Audit JSON exported: {out}")

        return 0 if failures == 0 else 1
