"""
System information module.

This module collects basic operating system information.
"""

import getpass
import platform

from .models import SystemInfo


def get_system_info() -> SystemInfo:
    """
    Collect system information.

    Returns
    -------
    SystemInfo
        Object containing system details.
    """

    return SystemInfo(
        hostname=platform.node(),
        operating_system=f"{platform.system()} {platform.release()}",
        kernel=platform.version(),
        architecture=platform.machine(),
        python_version=platform.python_version(),
        current_user=getpass.getuser(),
    )