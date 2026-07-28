"""
Command registry.
"""

from typing import Dict, Optional
from itat.core.command import Command


class CommandRegistry:
    """
    Registry for managing available CLI commands.
    """

    def __init__(self):
        self._commands: Dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """
        Register a new command.
        """
        self._commands[command.name] = command

    def get(self, name: str) -> Optional[Command]:
        """
        Get a registered command by name.
        """
        return self._commands.get(name)

    def list_all(self) -> Dict[str, Command]:
        """
        List all registered commands.
        """
        return self._commands.copy()