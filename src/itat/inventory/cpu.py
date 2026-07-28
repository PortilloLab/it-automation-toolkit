"""
CPU Collector.

Collects CPU information.
"""

import platform

import psutil

from .models import CPUInfo


def collect() -> CPUInfo:
    """
    Collect CPU information.
    """

    frequency = psutil.cpu_freq()

    return CPUInfo(
        processor=platform.processor() or platform.uname().processor or "Unknown",
        architecture=platform.machine(),
        physical_cores=psutil.cpu_count(logical=False) or 0,
        logical_cores=psutil.cpu_count(logical=True) or 0,
        current_frequency=round(frequency.current, 2) if frequency else 0.0,
    )