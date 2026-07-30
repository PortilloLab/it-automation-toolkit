"""
Base classes for CLI commands.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class Command(ABC):
    """
    Base class for every CLI command.
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, args: List[str]) -> int:
        """
        Execute the command.

        Parameters
        ----------
        args : List[str]
            Command arguments.

        Returns
        -------
        int
            Exit code (0 = success).
        """
        raise NotImplementedError

    def _get_arg_value(self, args: List[str], flag: str) -> Optional[str]:
        """
        Utility method to extract the value following a flag in CLI args.
        """
        if flag in args:
            idx = args.index(flag)
            if idx + 1 < len(args):
                return args[idx + 1]
        return None