"""
Unit tests for ITAT Interactive UI Menu.
"""

from itat.core.application import Application
from itat.ui.menu import InteractiveMenu


def test_interactive_menu_init():
    app = Application()
    app.initialize()
    menu = InteractiveMenu(app)
    assert menu.app == app


if __name__ == "__main__":
    test_interactive_menu_init()
    print("All UI unit tests passed!")
