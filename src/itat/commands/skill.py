from typing import List, Optional
from itat.core.command import Command
from itat.tickets import TicketDatabase
from itat.skills import (
    SkillManager,
    WebServiceSkill,
    MySQLSkill,
    PowerBISkill,
    PostgreSQLSkill,
    DockerSkill,
    SkillStatus,
)


class SkillCommand(Command):
    """
    Skill command to manage and execute client support skills.
    """

    name = "skill"
    description = "Execute specialized support skills for client applications."

    def __init__(self):
        super().__init__()
        self.manager = SkillManager()
        self.ticket_db = TicketDatabase()
        # Register built-in skills
        self.manager.register(WebServiceSkill(service_name="nginx"))
        self.manager.register(DockerSkill())
        self.manager.register(MySQLSkill())
        self.manager.register(PostgreSQLSkill())
        self.manager.register(PowerBISkill())

    def run(self, args: Optional[List[str]] = None) -> int:
        args = args or []
        subcommand = args[0] if args else "list"

        if subcommand in ("list", "--list"):
            return self._handle_list()
        elif subcommand in ("health", "check"):
            skill_name = self._get_arg_value(args, "--name") or self._get_arg_value(args, "-n")
            return self._handle_health(skill_name)
        elif subcommand in ("logs", "analyze"):
            skill_name = self._get_arg_value(args, "--name") or self._get_arg_value(args, "-n")
            log_path = self._get_arg_value(args, "--path") or self._get_arg_value(args, "-p")
            return self._handle_logs(skill_name, log_path)
        elif subcommand in ("fix", "autofix"):
            skill_name = self._get_arg_value(args, "--name") or self._get_arg_value(args, "-n")
            if not skill_name and len(args) > 1 and not args[1].startswith("-"):
                skill_name = args[1]
            auto_yes = "--yes" in args or "-y" in args
            return self._handle_fix(skill_name, auto_yes)
        else:
            print(f"Unknown skill subcommand: '{subcommand}'")
            print("Usage: itat skill [list | health | logs | fix] [--name <skill_name>] [--yes]")
            return 1

    def _handle_list(self) -> int:
        skills = self.manager.list_skills()
        print("=" * 60)
        print("IT Automation Toolkit - Registered Support Skills")
        print("=" * 60)
        if not skills:
            print("No skills currently registered.")
            return 0
        for s in skills:
            print(f"• Name           : {s['name']}")
            print(f"  Target Service : {s['target_service']}")
            print(f"  Description    : {s['description']}")
            print(f"  Version        : {s['version']}")
            print("-" * 60)
        return 0

    def _handle_health(self, skill_name: Optional[str]) -> int:
        print("=" * 60)
        print("ITAT Skills - Health Diagnostics")
        print("=" * 60)
        results = self.manager.run_health_checks(skill_name)
        for name, res in results.items():
            symbol = "[ OK ]" if res.status == SkillStatus.OK else f"[{res.status.value}]"
            print(f"{symbol} Skill: {name}")
            print(f"       Message: {res.message}")
            if res.recommendations:
                for rec in res.recommendations:
                    print(f"       ➜ Recommendation: {rec}")
            print("-" * 60)
        return 0

    def _handle_logs(self, skill_name: Optional[str], log_path: Optional[str]) -> int:
        print("=" * 60)
        print("ITAT Skills - Log Analysis")
        print("=" * 60)
        results = self.manager.run_log_analysis(skill_name, log_path)
        for name, res in results.items():
            symbol = "[ OK ]" if res.status == SkillStatus.OK else f"[{res.status.value}]"
            print(f"{symbol} Skill: {name}")
            print(f"       Message: {res.message}")
            if res.details.get("sample_errors"):
                print("       Recent Errors:")
                for err in res.details["sample_errors"]:
                    print(f"         - {err}")
            print("-" * 60)
        return 0

    def _handle_fix(self, skill_name: Optional[str], auto_yes: bool = False) -> int:
        if not skill_name:
            print("Error: Specify a skill name to fix, e.g.: itat skill fix --name web_service --yes")
            return 1

        if not auto_yes:
            print(f"⚠️  WARNING: Executing auto-fix for '{skill_name}' may restart services on this machine.")
            confirm = input("Are you sure you want to proceed? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Aborted auto-fix execution.")
                return 0

        print("=" * 60)
        print(f"ITAT Skills - Executing Auto-Fix for '{skill_name}'")
        print("=" * 60)
        res = self.manager.run_auto_fix(skill_name)
        symbol = "[ OK ]" if res.status == SkillStatus.OK else f"[{res.status.value}]"
        print(f"{symbol} Result: {res.message}")
        if res.actions_taken:
            for act in res.actions_taken:
                print(f"       ✔ Action taken: {act}")

        # Integrate with TicketDatabase: Auto-log incident/remediation ticket
        try:
            t_id = self.ticket_db.create_ticket(
                title=f"Auto-Fix remediation for skill '{skill_name}'",
                description=f"Message: {res.message}\nActions: {', '.join(res.actions_taken or ['None'])}",
                client_name="Local System",
                priority="HIGH" if res.status != SkillStatus.OK else "MEDIUM",
                skill_name=skill_name,
            )
            if res.status == SkillStatus.OK:
                self.ticket_db.resolve_ticket(t_id, notes=f"Resolved via ITAT auto_fix for '{skill_name}'")
                print(f"🎫 Auto-logged and resolved Ticket #{t_id} in ITAT Helpdesk DB.")
            else:
                print(f"🎫 Auto-logged open incident Ticket #{t_id} in ITAT Helpdesk DB.")
        except Exception as e:
            print(f"[!] Warning: Unable to auto-log ticket: {e}")

        print("=" * 60)
        return 0
