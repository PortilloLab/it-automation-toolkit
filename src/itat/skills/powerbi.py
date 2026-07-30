"""
PowerBI On-Premises Gateway Support Skill for ITAT framework.

Provides specialized diagnostics, log analysis, and automated remediation for Power BI Data Gateways.
"""

import os
import socket
import subprocess
from typing import Optional
from .base import BaseSkill, SkillResult, SkillStatus


class PowerBISkill(BaseSkill):
    """
    Skill for inspecting, diagnosing, and maintaining Power BI On-Premises Data Gateway.
    """

    name = "powerbi"
    description = "Specialized support skill for Power BI Data Gateway & Cloud Connectivity"
    version = "1.0.0"
    target_service = "powerbi-gateway"

    def __init__(
        self,
        service_name: str = "PBIEgwService",
        cloud_endpoint: str = "api.powerbi.com",
    ):
        self.service_name = service_name
        self.cloud_endpoint = cloud_endpoint
        self.target_service = service_name

    def check_health(self) -> SkillResult:
        """Check cloud connectivity and Gateway service health."""
        details = {
            "service": self.service_name,
            "cloud_endpoint": self.cloud_endpoint,
        }
        recommendations = []

        # 1. Test HTTPS cloud connectivity to PowerBI API
        cloud_ok = self._check_cloud_connectivity()
        details["cloud_reachable"] = cloud_ok

        # 2. Check Gateway service status
        gateway_active = self._check_gateway_active()
        details["gateway_active"] = gateway_active

        if cloud_ok and gateway_active:
            return SkillResult(
                status=SkillStatus.OK,
                message=f"Power BI Gateway '{self.service_name}' is active and cloud endpoint '{self.cloud_endpoint}' is reachable.",
                details=details,
            )
        elif not cloud_ok:
            recommendations.append("Check outbound HTTPS (port 443) rules and proxy settings for api.powerbi.com.")
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Unable to reach Power BI cloud endpoint '{self.cloud_endpoint}'. Network or DNS issue.",
                details=details,
                recommendations=recommendations,
            )
        else:
            recommendations.append(f"Run 'itat skill fix powerbi' or 'systemctl restart {self.service_name}'.")
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Cloud is reachable, but Power BI Gateway service '{self.service_name}' is stopped or inactive.",
                details=details,
                recommendations=recommendations,
            )

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 100) -> SkillResult:
        """Analyze Power BI Gateway log files for refresh errors or authentication failures."""
        possible_log_dirs = [
            log_path,
            "/var/log/powerbi",
            os.path.expanduser("~/AppData/Local/Microsoft/On-premises data gateway"),
        ]

        target_log = None
        for path in possible_log_dirs:
            if path and os.path.exists(path):
                target_log = path
                break

        error_lines = []

        if target_log and os.path.isfile(target_log):
            try:
                with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                    recent = f.readlines()[-lines:]
                    for line in recent:
                        if any(kw in line.lower() for kw in ["error", "exception", "failed", "unauthorized", "timeout"]):
                            error_lines.append(line.strip())
            except Exception as e:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Failed to read Gateway log: {str(e)}",
                )
        else:
            # Fallback to systemctl / journalctl check for Linux-hosted containers/services
            try:
                res = subprocess.run(
                    ["journalctl", "-u", self.service_name, "-n", str(lines), "--no-pager"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if any(kw in line.lower() for kw in ["error", "failed", "unauthorized"]):
                            error_lines.append(line)
            except Exception:
                pass

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} warning/error entries in Power BI Gateway logs.",
                details={"error_count": len(error_lines), "sample_errors": error_lines[:5]},
                recommendations=["Verify Power BI Service Data Source credentials or refresh tokens."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message="No critical error entries found in Power BI Gateway logs.",
        )

    def auto_fix(self) -> SkillResult:
        """Attempt automated remediation for Power BI Gateway."""
        health = self.check_health()
        if health.is_healthy():
            return SkillResult(
                status=SkillStatus.OK,
                message="Power BI Gateway is running healthily. No action needed.",
            )

        actions = []
        try:
            res = subprocess.run(
                ["sudo", "systemctl", "restart", self.service_name],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if res.returncode == 0:
                actions.append(f"Restarted Power BI Gateway service '{self.service_name}'.")
                return SkillResult(
                    status=SkillStatus.OK,
                    message=f"Successfully restarted Power BI Gateway service '{self.service_name}'.",
                    actions_taken=actions,
                )
            else:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Failed to restart Gateway service: {res.stderr.strip()}",
                )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"Power BI auto-fix exception: {str(e)}",
            )

    def _check_cloud_connectivity(self) -> bool:
        try:
            with socket.create_connection((self.cloud_endpoint, 443), timeout=3):
                return True
        except (socket.timeout, OSError):
            return False

    def _check_gateway_active(self) -> bool:
        try:
            res = subprocess.run(
                ["systemctl", "is-active", self.service_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return res.stdout.strip() == "active"
        except Exception:
            # If status cannot be determined (e.g. systemctl missing, permission error),
            # fail closed: report as NOT active rather than assuming healthy.
            return False
