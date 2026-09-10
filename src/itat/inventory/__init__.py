"""
System Inventory collectors package.
"""

from .scanner import scan
from .users import collect_user_inventory, UserInventory
from .export import export_json, export_markdown
from .models import (
    SystemInfo,
    CPUInfo,
    MemoryInfo,
    DiskInfo,
    DiskPartitionInfo,
    NetworkInfo,
    NetworkInterfaceInfo,
)

__all__ = [
    "scan",
    "collect_user_inventory",
    "UserInventory",
    "export_json",
    "export_markdown",
    "SystemInfo",
    "CPUInfo",
    "MemoryInfo",
    "DiskInfo",
    "DiskPartitionInfo",
    "NetworkInfo",
    "NetworkInterfaceInfo",
]
