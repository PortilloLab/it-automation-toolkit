"""
PostgreSQL Support Skill for ITAT framework.

Provides specialized diagnostics, log analysis, and automated remediation for PostgreSQL Database Server.
"""

import os
import socket
import subprocess
from typing import Optional
from .base import BaseSkill, SkillResult, SkillStatus
from itat.utils.services import ServiceManager


class PostgreSQLSkill(BaseSkill):
    """
    Skill for inspecting, diagnosing, and maintaining PostgreSQL Database Server.
    """

    name = "postgresql"
    description = "Specialized support skill for PostgreSQL Database Server"
    version = "1.0.0"
    target_service = "postgresql"

    def __init__(self, host: str = "127.0.0.1", port: int = 5432, service_name: str = "postgresql"):
        self.host = host
        self.port = port
        self.service_name = service_name

    def check_health(self) -> SkillResult:
        """Check PostgreSQL system service and TCP port 5432 accessibility."""
        details = {"host": self.host, "port": self.port, "service": self.service_name}
        recommendations = []

        port_open = self._check_port_open()
        details["port_listening"] = port_open

        service_active = ServiceManager.is_service_active(self.service_name)
        details["service_active"] = service_active

        if port_open and service_active:
            return SkillResult(
                status=SkillStatus.OK,
                message=f"PostgreSQL Server is active and listening on {self.host}:{self.port}.",
                details=details,
            )
        elif service_active and not port_open:
            recommendations.append(f"Verify PostgreSQL listen_addresses in postgresql.conf or firewall rules for port {self.port}.")
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"PostgreSQL service is active, but port {self.port} is not accepting connections.",
                details=details,
                recommendations=recommendations,
            )
        else:
            recommendations.append(f"Run 'itat skill fix postgresql' or start service '{self.service_name}'.")
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"PostgreSQL Server service '{self.service_name}' is stopped or not running.",
                details=details,
                recommendations=recommendations,
            )

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 100) -> SkillResult:
        """Analyze PostgreSQL error logs or journalctl for critical entries."""
        possible_paths = [
            log_path,
            "/var/log/postgresql/postgresql-main.log",
            "/var/log/postgresql/postgresql.log",
        ]

        target_log = None
        for path in possible_paths:
            if path and os.path.exists(path):
                target_log = path
                break

        error_lines = []

        if target_log:
            try:
                with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                    recent = f.readlines()[-lines:]
                    for line in recent:
                        if any(kw in line.lower() for kw in ["fatal", "panic", "error", "connection refused", "corrupted"]):
                            error_lines.append(line.strip())
            except Exception as e:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Error reading PostgreSQL log file {target_log}: {str(e)}",
                )
        else:
            try:
                res = subprocess.run(
                    ["journalctl", "-u", self.service_name, "-n", str(lines), "--no-pager"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if any(kw in line.lower() for kw in ["fatal", "error", "panic", "failed"]):
                            error_lines.append(line)
            except Exception:
                pass

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} warning/error log entries in PostgreSQL.",
                details={"log_file": target_log or "journalctl", "error_count": len(error_lines), "sample_errors": error_lines[:5]},
                recommendations=["Inspect PostgreSQL connection pool limits, disk quota, or client authentication."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message="No critical error entries found in recent PostgreSQL logs.",
            details={"log_file": target_log or "journalctl"},
        )

    def auto_fix(self) -> SkillResult:
        """Attempt automated remediation (restart PostgreSQL service)."""
        health = self.check_health()
        if health.is_healthy():
            return SkillResult(
                status=SkillStatus.OK,
                message="PostgreSQL is already running healthily. No remediation needed.",
            )

        success, msg = ServiceManager.restart_service(self.service_name, timeout=15)
        if success:
            actions = [f"Restarted '{self.service_name}' service via ServiceManager."]
            post_check = self.check_health()
            if post_check.is_healthy():
                return SkillResult(
                    status=SkillStatus.OK,
                    message=f"Successfully restored PostgreSQL Server '{self.service_name}'.",
                    actions_taken=actions,
                )
            else:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message="Restart command executed, but PostgreSQL health check is still failing.",
                    actions_taken=actions,
                )
        else:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=msg,
            )

    def _check_port_open(self) -> bool:
        try:
            with socket.create_connection((self.host, self.port), timeout=2):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False
