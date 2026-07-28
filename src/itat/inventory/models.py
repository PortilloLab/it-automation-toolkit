"""
Inventory data models.
"""

from dataclasses import dataclass


@dataclass
class SystemInfo:

    hostname: str
    operating_system: str
    kernel: str
    architecture: str
    python_version: str
    current_user: str


@dataclass
class CPUInfo:

    processor: str
    architecture: str
    physical_cores: int
    logical_cores: int
    current_frequency: float


@dataclass
class MemoryInfo:

    total_gb: float
    available_gb: float
    used_gb: float
    used_percent: float
    swap_total_gb: float
    swap_used_gb: float
    swap_percent: float


@dataclass
class DiskPartitionInfo:

    device: str
    mountpoint: str
    fstype: str
    total_gb: float
    used_gb: float
    free_gb: float
    used_percent: float


@dataclass
class DiskInfo:

    partitions: list[DiskPartitionInfo]


@dataclass
class NetworkInterfaceInfo:

    interface: str
    ip_address: str
    mac_address: str
    is_up: bool


@dataclass
class NetworkInfo:

    interfaces: list[NetworkInterfaceInfo]