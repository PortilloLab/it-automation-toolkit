"""
CPU Collector.

Collects CPU information.
"""

import platform

import psutil

from .models import CPUInfo


def _get_processor_name() -> str:
    """Extract human-readable CPU model name."""
    name = platform.processor() or platform.uname().processor
    if name and name.strip() and name.strip() != "x86_64":
        return name.strip()

    try:
        with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass

    return platform.machine() or "Unknown"


def collect() -> CPUInfo:
    """
    Collect CPU information.
    """

    frequency = psutil.cpu_freq()

    return CPUInfo(
        processor=_get_processor_name(),
        architecture=platform.machine(),
        physical_cores=psutil.cpu_count(logical=False) or 0,
        logical_cores=psutil.cpu_count(logical=True) or 0,
        current_frequency=round(frequency.current, 2) if frequency else 0.0,
    )