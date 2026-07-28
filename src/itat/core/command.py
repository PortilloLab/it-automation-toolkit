"""
Base classes for CLI commands.
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Base class for every CLI command.
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, args: list[str]) -> int:
        """
        Execute the command.

        Parameters
        ----------
        args : list[str]
            Command arguments.

        Returns
        -------
        int
            Exit code (0 = success).
        """
        raise NotImplementedError