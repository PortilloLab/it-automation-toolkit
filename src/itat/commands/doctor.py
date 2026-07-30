"""
Doctor command for system health diagnostics.
"""

import socket
import psutil
from itat.core.command import Command
from itat.i18n import t


class DoctorCommand(Command):
    """
    Doctor command performs system diagnostics and health checks.
    """

    name = "doctor"
    description = "Perform system health checks and diagnostics."

    def run(self, args: list[str]) -> int:
        print("=" * 60)
        print(f"IT Automation Toolkit - {t('doctor')}")
        print("=" * 60)

        checks_passed = 0
        checks_warn = 0
        checks_fail = 0

        # Check 1: CPU Usage
        cpu_percent = psutil.cpu_percent(interval=0.5)
        if cpu_percent < 80.0:
            status = "[ OK ]"
            checks_passed += 1
            msg = f"CPU Load is normal ({cpu_percent}%)"
        elif cpu_percent < 95.0:
            status = "[ WARN ]"
            checks_warn += 1
            msg = f"CPU Load is high ({cpu_percent}%)"
        else:
            status = "[ FAIL ]"
            checks_fail += 1
            msg = f"CPU Load is CRITICAL ({cpu_percent}%)"
        print(f"{status:<8} CPU Load         : {msg}")

        # Check 2: Memory (RAM) Usage
        mem = psutil.virtual_memory()
        if mem.percent < 85.0:
            status = "[ OK ]"
            checks_passed += 1
            msg = f"RAM Usage is healthy ({mem.percent}%)"
        elif mem.percent < 95.0:
            status = "[ WARN ]"
            checks_warn += 1
            msg = f"RAM Usage is high ({mem.percent}%)"
        else:
            status = "[ FAIL ]"
            checks_fail += 1
            msg = f"RAM Usage is CRITICAL ({mem.percent}%)"
        print(f"{status:<8} RAM Usage        : {msg}")

        # Check 3: Root Disk Space
        try:
            root_disk = psutil.disk_usage("/")
            if root_disk.percent < 85.0:
                status = "[ OK ]"
                checks_passed += 1
                msg = f"Root Disk Space is healthy ({root_disk.percent}% used)"
            elif root_disk.percent < 95.0:
                status = "[ WARN ]"
                checks_warn += 1
                msg = f"Root Disk Space is running low ({root_disk.percent}% used)"
            else:
                status = "[ FAIL ]"
                checks_fail += 1
                msg = f"Root Disk Space is CRITICAL ({root_disk.percent}% used)"
        except Exception as e:
            status = "[ FAIL ]"
            checks_fail += 1
            msg = f"Unable to check root disk: {e}"
        print(f"{status:<8} Root Storage     : {msg}")

        # Check 4: Network Connectivity
        try:
            socket.setdefaulttimeout(3)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(("8.8.8.8", 53))
            status = "[ OK ]"
            checks_passed += 1
            msg = "Internet connectivity active (DNS reachable)"
        except Exception:
            status = "[ WARN ]"
            checks_warn += 1
            msg = "No internet connectivity detected"
        print(f"{status:<8} Connectivity     : {msg}")

        # Check 5: System Load Average (Unix)
        if hasattr(psutil, "getloadavg"):
            load1, load5, load15 = psutil.getloadavg()
            status = "[ OK ]"
            checks_passed += 1
            msg = f"Load average (1m, 5m, 15m): {load1:.2f}, {load5:.2f}, {load15:.2f}"
            print(f"{status:<8} Load Average     : {msg}")

        print("-" * 60)
        print(f"Summary: {checks_passed} {t('passed')} | {checks_warn} {t('warnings')} | {checks_fail} {t('failures')}")
        print("-" * 60)

        return 0 if checks_fail == 0 else 1
