"""
Disk Collector.

Collects information about disk partitions and storage usage.
"""

import psutil

from .models import DiskInfo, DiskPartitionInfo


def collect() -> DiskInfo:
    """
    Collect information about system disk partitions.
    """
    partitions_info: list[DiskPartitionInfo] = []
    bytes_in_gb = 1024**3

    for partition in psutil.disk_partitions(all=False):
        # Ignore snap loop devices and squashfs mounts
        if partition.device.startswith("/dev/loop") or partition.fstype == "squashfs":
            continue

        try:
            usage = psutil.disk_usage(partition.mountpoint)
            partitions_info.append(
                DiskPartitionInfo(
                    device=partition.device,
                    mountpoint=partition.mountpoint,
                    fstype=partition.fstype,
                    total_gb=round(usage.total / bytes_in_gb, 2),
                    used_gb=round(usage.used / bytes_in_gb, 2),
                    free_gb=round(usage.free / bytes_in_gb, 2),
                    used_percent=usage.percent,
                )
            )
        except (PermissionError, OSError):
            continue

    return DiskInfo(partitions=partitions_info)

