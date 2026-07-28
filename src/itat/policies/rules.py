"""
Built-in system policies and rules.
"""

from typing import Any, Dict
from .base import Policy, PolicyResult


class DiskSpacePolicy(Policy):
    """
    Ensures storage usage does not exceed maximum threshold.
    """

    name = "Disk Space Compliance"
    description = "Checks if disk partitions exceed storage threshold."
    severity = "HIGH"

    def __init__(self, max_usage_percent: float = 85.0):
        self.max_usage_percent = max_usage_percent

    def evaluate(self, inventory: Dict[str, Any]) -> PolicyResult:
        disk_data = inventory.get("disk", {})
        partitions = getattr(disk_data, "partitions", []) if hasattr(disk_data, "partitions") else disk_data.get("partitions", [])

        violations = []
        for part in partitions:
            used_pct = getattr(part, "used_percent", None) if hasattr(part, "used_percent") else part.get("used_percent")
            mount = getattr(part, "mountpoint", None) if hasattr(part, "mountpoint") else part.get("mountpoint")
            if used_pct is not None and used_pct > self.max_usage_percent:
                violations.append(f"{mount} ({used_pct}%)")

        if violations:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Partitions exceeding threshold ({self.max_usage_percent}%): {', '.join(violations)}",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            severity=self.severity,
            message=f"All disk partitions are within limit (< {self.max_usage_percent}%).",
        )


class MemoryUsagePolicy(Policy):
    """
    Ensures RAM usage is below threshold.
    """

    name = "RAM Usage Compliance"
    description = "Checks if system memory usage is below threshold."
    severity = "MEDIUM"

    def __init__(self, max_usage_percent: float = 85.0):
        self.max_usage_percent = max_usage_percent

    def evaluate(self, inventory: Dict[str, Any]) -> PolicyResult:
        mem_data = inventory.get("memory", {})
        used_pct = getattr(mem_data, "used_percent", None) if hasattr(mem_data, "used_percent") else mem_data.get("used_percent")

        if used_pct is not None and used_pct > self.max_usage_percent:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"RAM usage is high: {used_pct}% (Limit: {self.max_usage_percent}%)",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            severity=self.severity,
            message=f"RAM usage is within limit: {used_pct}%",
        )


class UserSecurityPolicy(Policy):
    """
    Ensures non-root user execution policy.
    """

    name = "User Privilege Policy"
    description = "Audits active user privilege level."
    severity = "LOW"

    def evaluate(self, inventory: Dict[str, Any]) -> PolicyResult:
        sys_data = inventory.get("system", {})
        user = getattr(sys_data, "current_user", None) if hasattr(sys_data, "current_user") else sys_data.get("current_user")

        if user == "root":
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                severity="MEDIUM",
                message="System operations running under root account",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            severity=self.severity,
            message=f"System running under standard user '{user}'",
        )
