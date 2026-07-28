"""
MySQL Support Skill for ITAT framework.

Provides specialized diagnostics, log analysis, and automated remediation for MySQL Database Server.
"""

import os
import socket
import subprocess
from typing import Optional
from .base import BaseSkill, SkillResult, SkillStatus


class MySQLSkill(BaseSkill):
    """
    Skill for inspecting, diagnosing, and maintaining MySQL / MariaDB Server.
    """

    name = "mysql"
    description = "Specialized support skill for MySQL / MariaDB Database Server"
    version = "1.0.0"
    target_service = "mysql"

    def __init__(self, host: str = "127.0.0.1", port: int = 3306, service_name: str = "mysql"):
        self.host = host
        self.port = port
        self.service_name = service_name

    def check_health(self) -> SkillResult:
        """Check MySQL system service and port 3306 accessibility."""
        details = {"host": self.host, "port": self.port, "service": self.service_name}
        recommendations = []

        # 1. Check TCP socket connectivity on MySQL port
        port_open = self._check_port_open()
        details["port_listening"] = port_open

        # 2. Check service status via systemctl
        service_active = self._check_service_active()
        details["service_active"] = service_active

        if port_open and service_active:
            return SkillResult(
                status=SkillStatus.OK,
                message=f"MySQL Server is active and listening on {self.host}:{self.port}.",
                details=details,
            )
        elif service_active and not port_open:
            recommendations.append("Verify MySQL bind-address or check if port 3306 is blocked by firewall.")
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"MySQL service is active, but port {self.port} is not accepting connections.",
                details=details,
                recommendations=recommendations,
            )
        else:
            recommendations.append(f"Run 'itat skill fix mysql' or 'sudo systemctl start {self.service_name}'.")
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"MySQL Server service '{self.service_name}' is stopped or not running.",
                details=details,
                recommendations=recommendations,
            )

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 100) -> SkillResult:
        """Analyze MySQL error log files or journalctl for critical errors."""
        possible_paths = [
            log_path,
            "/var/log/mysql/error.log",
            "/var/log/mysqld.log",
            "/var/log/mariadb/mariadb.log",
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
                        if any(kw in line.lower() for kw in ["[error]", "[critical]", "access denied", "corrupted"]):
                            error_lines.append(line.strip())
            except Exception as e:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Error reading log file {target_log}: {str(e)}",
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
                if res.returncode == 0:
                    for line in res.stdout.splitlines():
                        if any(kw in line.lower() for kw in ["error", "fail", "denied", "crash"]):
                            error_lines.append(line)
            except Exception:
                pass

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} potential issue entries in MySQL log.",
                details={"log_file": target_log or "journalctl", "error_count": len(error_lines), "sample_errors": error_lines[:5]},
                recommendations=["Inspect table integrity with 'mysqlcheck' or review user credentials."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message="No critical error entries found in recent MySQL logs.",
            details={"log_file": target_log or "journalctl"},
        )

    def auto_fix(self) -> SkillResult:
        """Attempt automated remediation (restart MySQL service)."""
        health = self.check_health()
        if health.is_healthy():
            return SkillResult(
                status=SkillStatus.OK,
                message="MySQL is already running normally. No remediation needed.",
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
                actions.append(f"Restarted '{self.service_name}' service via systemctl.")
                # Verify after restart
                post_check = self.check_health()
                if post_check.is_healthy():
                    return SkillResult(
                        status=SkillStatus.OK,
                        message=f"Successfully restored MySQL Server '{self.service_name}'.",
                        actions_taken=actions,
                    )
                else:
                    return SkillResult(
                        status=SkillStatus.ERROR,
                        message="Restarted service, but MySQL port/health check is still failing.",
                        actions_taken=actions,
                    )
            else:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Failed restarting MySQL: {res.stderr.strip()}",
                )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"MySQL auto-fix exception: {str(e)}",
            )

    def _check_port_open(self) -> bool:
        try:
            with socket.create_connection((self.host, self.port), timeout=2):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def _check_service_active(self) -> bool:
        try:
            res = subprocess.run(
                ["systemctl", "is-active", self.service_name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return res.stdout.strip() == "active"
        except Exception:
            return False
