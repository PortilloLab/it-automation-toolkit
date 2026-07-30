"""
System Inventory collectors package.
"""

from .users import collect_user_inventory, UserInventory

__all__ = [
    "collect_user_inventory",
    "UserInventory",
]
