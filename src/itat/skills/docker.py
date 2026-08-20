"""
Docker Ecosystem Support Skill for ITAT framework.

Provides deep container inspection, daemon health checks, crashed container diagnostics, and remediation.
"""

import subprocess
from typing import Optional
from .base import BaseSkill, SkillResult, SkillStatus
from itat.utils.services import ServiceManager


class DockerSkill(BaseSkill):
    """
    Skill for inspecting, diagnosing, and maintaining Docker Engine and Container stack.
    """

    name = "docker"
    description = "Specialized support skill for Docker Daemon & Container Ecosystem"
    version = "1.0.0"
    target_service = "docker"

    def __init__(self, service_name: str = "docker"):
        self.service_name = service_name

    def check_health(self) -> SkillResult:
        """Check Docker daemon status and inspect running/exited containers."""
        details = {"service": self.service_name}
        recommendations = []

        daemon_active = ServiceManager.is_service_active(self.service_name)
        details["daemon_active"] = daemon_active

        if not daemon_active:
            recommendations.append(f"Run 'itat skill fix docker' or start '{self.service_name}' service.")
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"Docker daemon service '{self.service_name}' is stopped or inactive.",
                details=details,
                recommendations=recommendations,
            )

        # Inspect containers via `docker ps -a`
        try:
            res = subprocess.run(
                ["docker", "ps", "-a", "--format", "{{.ID}}|{{.Names}}|{{.Status}}|{{.State}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode != 0:
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"Docker daemon is running, but 'docker ps' failed: {res.stderr.strip()}",
                    details=details,
                )

            container_lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
            total_containers = len(container_lines)
            running_containers = [l for l in container_lines if "|running" in l.lower()]
            exited_containers = [l for l in container_lines if "|exited" in l.lower()]

            details["total_containers"] = total_containers
            details["running_containers"] = len(running_containers)
            details["exited_containers"] = len(exited_containers)

            if exited_containers:
                recommendations.append(f"Found {len(exited_containers)} exited/crashed container(s). Review logs with 'itat skill logs --name docker'.")
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"Docker daemon active with {len(running_containers)}/{total_containers} running. {len(exited_containers)} container(s) exited.",
                    details=details,
                    recommendations=recommendations,
                )

            return SkillResult(
                status=SkillStatus.OK,
                message=f"Docker daemon active with {len(running_containers)}/{total_containers} container(s) running healthily.",
                details=details,
            )

        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Docker CLI health inspection error: {str(e)}",
                details=details,
            )

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 50) -> SkillResult:
        """Analyze Docker daemon logs and recent exited container logs."""
        error_lines = []

        # 1. Check journalctl for docker daemon
        try:
            res = subprocess.run(
                ["journalctl", "-u", self.service_name, "-n", str(lines), "--no-pager"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if any(kw in line.lower() for kw in ["error", "fatal", "failed", "died"]):
                        error_lines.append(f"[Daemon] {line}")
        except Exception:
            pass

        # 2. Check logs of exited containers
        try:
            res_exited = subprocess.run(
                ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.ID}}|{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res_exited.returncode == 0:
                exited = [l.strip() for l in res_exited.stdout.splitlines() if l.strip()]
                for item in exited[:3]:  # Top 3 exited containers
                    parts = item.split("|")
                    c_id, c_name = parts[0], parts[1]
                    res_log = subprocess.run(
                        ["docker", "logs", "--tail", "10", c_id],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    c_output = res_log.stderr.strip() or res_log.stdout.strip()
                    if c_output:
                        error_lines.append(f"[Container '{c_name}'] {c_output[-150:]}")
        except Exception:
            pass

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} warning/error entries across Docker daemon and containers.",
                details={"error_count": len(error_lines), "sample_errors": error_lines[:5]},
                recommendations=["Check container restart policy or application configurations."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message="No critical error entries found in Docker daemon or container logs.",
        )

    def auto_fix(self) -> SkillResult:
        """Attempt automated remediation for Docker daemon or stopped containers."""
        health = self.check_health()
        if health.is_healthy():
            return SkillResult(
                status=SkillStatus.OK,
                message="Docker daemon and container stack are running healthily. No action needed.",
            )

        actions = []
        daemon_active = ServiceManager.is_service_active(self.service_name)
        if not daemon_active:
            success, msg = ServiceManager.restart_service(self.service_name, timeout=15)
            if success:
                actions.append(f"Restarted Docker service '{self.service_name}' via ServiceManager.")
            else:
                return SkillResult(status=SkillStatus.ERROR, message=msg)

        # Attempt to restart exited containers
        try:
            res_exited = subprocess.run(
                ["docker", "ps", "-a", "--filter", "status=exited", "--format", "{{.ID}}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res_exited.returncode == 0:
                c_ids = [c.strip() for c in res_exited.stdout.splitlines() if c.strip()]
                if c_ids:
                    res_restart = subprocess.run(
                        ["docker", "restart"] + c_ids,
                        capture_output=True,
                        text=True,
                        timeout=20,
                    )
                    if res_restart.returncode == 0:
                        actions.append(f"Restarted {len(c_ids)} exited Docker container(s).")
        except Exception:
            pass

        return SkillResult(
            status=SkillStatus.OK,
            message="Completed Docker auto-fix remediation.",
            actions_taken=actions or ["Inspected Docker state; no restart needed."],
        )
