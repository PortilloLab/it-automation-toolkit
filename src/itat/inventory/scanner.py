from .system import get_system_info
from .cpu import collect as cpu_collect
from .memory import collect as memory_collect
from .disk import collect as disk_collect
from .network import collect as network_collect
from .processes import collect_top_processes


def scan():

    return {
        "system": get_system_info(),
        "cpu": cpu_collect(),
        "memory": memory_collect(),
        "disk": disk_collect(),
        "network": network_collect(),
        "processes": collect_top_processes(5),
    }