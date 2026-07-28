"""
Application bootstrap.
"""

from itat.commands.inventory import InventoryCommand
from itat.commands.doctor import DoctorCommand
from itat.commands.audit import AuditCommand
from itat.commands.version import VersionCommand
from itat.commands.skill import SkillCommand
from itat.core.registry import CommandRegistry


class Application:
    """
    Main application class.
    """

    def __init__(self):
        self.registry = CommandRegistry()

    def initialize(self):
        """
        Register all application commands.
        """
        self.registry.register(InventoryCommand())
        self.registry.register(DoctorCommand())
        self.registry.register(AuditCommand())
        self.registry.register(VersionCommand())
        self.registry.register(SkillCommand())



    def execute(self, command_name: str, args: list[str]) -> int:
        """
        Execute a command by its name.
        """
        command = self.registry.get(command_name)

        if command is None:
            print(f"Unknown command: {command_name}")
            return 1

        return command.run(args)