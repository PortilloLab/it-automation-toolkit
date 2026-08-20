"""
Built-in skills for common IT services (e.g. Systemd Services, Web Server / Nginx).
"""

import os
import subprocess
from typing import Optional
from .base import BaseSkill, SkillResult, SkillStatus
from itat.utils.services import ServiceManager


class WebServiceSkill(BaseSkill):
    """
    Skill for inspecting and supporting local Web / HTTP services (e.g. Nginx, Apache, Systemd services).
    """

    name = "web_service"
    description = "Support skill for Web Servers (Nginx / Systemd HTTP services)"
    version = "1.0.0"
    target_service = "nginx"

    def __init__(self, service_name: str = "nginx"):
        self.name = service_name
        self.service_name = service_name
        self.target_service = service_name

    def check_health(self) -> SkillResult:
        """Check status of the web service using ServiceManager."""
        try:
            is_active = ServiceManager.is_service_active(self.service_name)
            if is_active:
                return SkillResult(
                    status=SkillStatus.OK,
                    message=f"Service '{self.service_name}' is active and running.",
                    details={"service": self.service_name, "active": True},
                )
            else:
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"Service '{self.service_name}' is inactive or stopped.",
                    details={"service": self.service_name, "active": False},
                    recommendations=[f"Run 'itat skill fix {self.name}' or restart service '{self.service_name}'"],
                )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Unable to query status for '{self.service_name}': {str(e)}",
                details={"error": str(e)},
            )

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 50) -> SkillResult:
        """Analyze journalctl or log file for error patterns."""
        target_log = log_path or f"/var/log/{self.service_name}/error.log"
        error_lines = []

        if os.path.exists(target_log):
            try:
                with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.readlines()[-lines:]
                    error_lines = [l.strip() for l in content if "error" in l.lower() or "crit" in l.lower()]
            except Exception as e:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Failed reading log file {target_log}: {str(e)}",
                )
        else:
            # Fallback to journalctl
            try:
                res = subprocess.run(
                    ["journalctl", "-u", self.service_name, "-n", str(lines), "--no-pager"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                output_lines = res.stdout.splitlines()
                error_lines = [l for l in output_lines if "error" in l.lower() or "fail" in l.lower()]
            except Exception:
                pass

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} warning/error log entries in {self.service_name}.",
                details={"error_count": len(error_lines), "sample_errors": error_lines[:5]},
                recommendations=["Inspect application configuration or restart service."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message=f"No critical errors found in recent logs for '{self.service_name}'.",
        )

    def auto_fix(self) -> SkillResult:
        """Attempt to restart the service using ServiceManager."""
        health = self.check_health()
        if health.is_healthy():
            return SkillResult(
                status=SkillStatus.OK,
                message=f"Service '{self.service_name}' is already healthy. No action required.",
            )

        success, msg = ServiceManager.restart_service(self.service_name)
        if success:
            return SkillResult(
                status=SkillStatus.OK,
                message=f"Successfully restarted service '{self.service_name}'.",
                actions_taken=[f"Restarted {self.service_name} via ServiceManager"],
            )
        else:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=msg,
            )
