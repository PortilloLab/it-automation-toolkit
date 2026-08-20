"""
Cross-platform Service Manager utility for ITAT.
Supports Linux (systemd), Windows (sc.exe / net), and macOS.
"""

import os
import platform
import subprocess
from typing import Tuple


class ServiceManager:
    """
    Cross-platform service inspection and management utility.
    """

    @staticmethod
    def is_service_active(service_name: str) -> bool:
        """
        Check if a system service is currently running.
        """
        system = platform.system().lower()

        if system == "linux":
            try:
                res = subprocess.run(
                    ["systemctl", "is-active", service_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return res.stdout.strip() == "active"
            except Exception:
                return False

        elif system == "windows":
            try:
                res = subprocess.run(
                    ["sc", "query", service_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return "RUNNING" in res.stdout
            except Exception:
                return False

        elif system == "darwin":  # macOS
            try:
                res = subprocess.run(
                    ["launchctl", "list", service_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return res.returncode == 0
            except Exception:
                return False

        return False

    @staticmethod
    def restart_service(service_name: str, timeout: int = 15) -> Tuple[bool, str]:
        """
        Attempt to restart a system service safely across OS platforms.

        :return: Tuple of (success_flag, status_or_error_message)
        """
        system = platform.system().lower()

        if system == "linux":
            # Check if running as root
            cmd = ["systemctl", "restart", service_name]
            if os.geteuid() != 0:
                cmd = ["sudo", "-n", "systemctl", "restart", service_name]

            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if res.returncode == 0:
                    return True, f"Service '{service_name}' restarted successfully."
                else:
                    err_msg = res.stderr.strip() or res.stdout.strip()
                    if "password is required" in err_msg.lower() or "a password is required" in err_msg.lower():
                        return False, f"Failed: Sudo password required for restarting '{service_name}'."
                    return False, f"Failed restarting '{service_name}': {err_msg}"
            except subprocess.TimeoutExpired:
                return False, f"Timeout after {timeout}s restarting '{service_name}'."
            except Exception as e:
                return False, f"Exception restarting '{service_name}': {str(e)}"

        elif system == "windows":
            try:
                res = subprocess.run(
                    ["net", "stop", service_name],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                res_start = subprocess.run(
                    ["net", "start", service_name],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )
                if res_start.returncode == 0:
                    return True, f"Windows service '{service_name}' restarted successfully."
                else:
                    return False, f"Failed starting Windows service '{service_name}': {res_start.stderr.strip()}"
            except Exception as e:
                return False, f"Exception restarting Windows service '{service_name}': {str(e)}"

        else:
            return False, f"Service management not supported on OS platform '{system}'."
