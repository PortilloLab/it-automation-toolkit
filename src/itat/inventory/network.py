"""
Network Collector.

Collects network interface information.
"""

import socket
import psutil

from .models import NetworkInfo, NetworkInterfaceInfo


def collect() -> NetworkInfo:
    """
    Collect network interface details.
    """
    interfaces_info: list[NetworkInterfaceInfo] = []
    stats = psutil.net_if_stats()
    addrs = psutil.net_if_addrs()

    for iface_name, iface_addrs in addrs.items():
        ip_addr = "N/A"
        mac_addr = "N/A"
        is_up = stats[iface_name].isup if iface_name in stats else False

        for addr in iface_addrs:
            if addr.family == socket.AF_INET:
                ip_addr = addr.address
            elif addr.family == psutil.AF_LINK or addr.family == getattr(socket, "AF_PACKET", -1):
                mac_addr = addr.address

        if ip_addr != "N/A" or mac_addr != "N/A":
            interfaces_info.append(
                NetworkInterfaceInfo(
                    interface=iface_name,
                    ip_address=ip_addr,
                    mac_address=mac_addr,
                    is_up=is_up,
                )
            )

    return NetworkInfo(interfaces=interfaces_info)
