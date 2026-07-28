"""
IT Automation Toolkit - Command Line Interface
"""

import sys

from itat.core.application import Application
from itat.version import (
    __title__,
    __version__,
    __author__,
    __organization__,
)


def main():

    app = Application()
    app.initialize()

    if len(sys.argv) == 1 or sys.argv[1] in ("--help", "-h", "help"):

        print("=" * 50)
        print(__title__)
        print(f"Version      : {__version__}")
        print(f"Author       : {__author__}")
        print(f"Organization : {__organization__}")
        print("=" * 50)

        print("\nAvailable commands:")

        commands_map = app.registry.list_all()
        for cmd_name, cmd_obj in commands_map.items():
            desc = getattr(cmd_obj, "description", "")
            print(f"  • {cmd_name:<12} : {desc}")

        print("\nUsage:")
        print("  itat <command> [options]\n")
        return

    command = sys.argv[1]

    exit_code = app.execute(
        command,
        sys.argv[2:]
    )

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()