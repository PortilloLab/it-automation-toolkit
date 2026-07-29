"""
IT Automation Toolkit - Command Line Interface & Interactive Platform
"""

import sys

from itat.core.application import Application
from itat.ui import InteractiveMenu
from itat.version import (
    __title__,
    __version__,
    __author__,
    __organization__,
)


def main():
    app = Application()
    app.initialize()

    # If no arguments provided, launch the Interactive Control Panel Menu
    if len(sys.argv) == 1 or sys.argv[1] in ("menu", "ui", "interactive"):
        menu = InteractiveMenu(app)
        try:
            menu.start()
        except KeyboardInterrupt:
            print("\n\nSaliendo de ITAT...")
            sys.exit(0)

    if sys.argv[1] in ("--help", "-h", "help"):
        print("=" * 60)
        print(f"🤖 {__title__}")
        print(f"   Version      : {__version__}")
        print(f"   Author       : {__author__}")
        print(f"   Organization : {__organization__}")
        print("=" * 60)

        print("\nAvailable commands:")
        commands_map = app.registry.list_all()
        for cmd_name, cmd_obj in commands_map.items():
            desc = getattr(cmd_obj, "description", "")
            print(f"  • {cmd_name:<12} : {desc}")

        print("\nUsage:")
        print("  itat                        (Launches Interactive Menu Platform)")
        print("  itat <command> [options]    (Executes CLI command directly)\n")
        return

    command = sys.argv[1]
    exit_code = app.execute(command, sys.argv[2:])
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()