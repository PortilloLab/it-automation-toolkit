"""
Process Collector.

Collects top resource-consuming processes.
"""

from dataclasses import dataclass
import psutil


@dataclass
class ProcessInfo:
    pid: int
    name: str
    username: str
    cpu_percent: float
    memory_percent: float


def collect_top_processes(limit: int = 5) -> list[ProcessInfo]:
    """
    Get top resource consuming processes by memory usage.
    """
    processes = []
    for proc in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_percent"]):
        try:
            info = proc.info
            processes.append(
                ProcessInfo(
                    pid=info["pid"],
                    name=info["name"] or "Unknown",
                    username=info["username"] or "N/A",
                    cpu_percent=round(info["cpu_percent"] or 0.0, 1),
                    memory_percent=round(info["memory_percent"] or 0.0, 1),
                )
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    processes.sort(key=lambda p: p.memory_percent, reverse=True)
    return processes[:limit]
