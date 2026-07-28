"""
Memory Collector.

Collects RAM and Swap memory information.
"""

import psutil

from .models import MemoryInfo


def collect() -> MemoryInfo:
    """
    Collect RAM and Swap memory information.
    """
    virtual_mem = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()

    bytes_in_gb = 1024**3

    return MemoryInfo(
        total_gb=round(virtual_mem.total / bytes_in_gb, 2),
        available_gb=round(virtual_mem.available / bytes_in_gb, 2),
        used_gb=round(virtual_mem.used / bytes_in_gb, 2),
        used_percent=virtual_mem.percent,
        swap_total_gb=round(swap_mem.total / bytes_in_gb, 2),
        swap_used_gb=round(swap_mem.used / bytes_in_gb, 2),
        swap_percent=swap_mem.percent,
    )
