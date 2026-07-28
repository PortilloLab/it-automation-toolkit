"""
Version command.
"""

from itat.core.command import Command
from itat.version import __version__


class VersionCommand(Command):
    """
    Version command to print framework version.
    """

    name = "version"
    description = "Show IT Automation Toolkit version."

    def run(self, args: list[str]) -> int:
        print(f"IT Automation Toolkit v{__version__}")
        return 0
