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
        partitions = disk_data.get("partitions", [])

        violations = []
        for part in partitions:
            used_pct = part.get("used_percent") if isinstance(part, dict) else getattr(part, "used_percent", None)
            mount = part.get("mountpoint") if isinstance(part, dict) else getattr(part, "mountpoint", None)
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
        used_pct = mem_data.get("used_percent") if isinstance(mem_data, dict) else getattr(mem_data, "used_percent", None)

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
        user = sys_data.get("current_user") if isinstance(sys_data, dict) else getattr(sys_data, "current_user", None)

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


class SwapUsagePolicy(Policy):
    """
    Ensures Swap usage does not indicate memory exhaustion.
    """

    name = "Swap Memory Health"
    description = "Checks if Swap usage exceeds critical threshold."
    severity = "MEDIUM"

    def __init__(self, max_usage_percent: float = 80.0):
        self.max_usage_percent = max_usage_percent

    def evaluate(self, inventory: Dict[str, Any]) -> PolicyResult:
        mem_data = inventory.get("memory", {})
        used_pct = mem_data.get("swap_percent") if isinstance(mem_data, dict) else getattr(mem_data, "swap_percent", None)

        if used_pct is not None and used_pct > self.max_usage_percent:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                severity=self.severity,
                message=f"Swap usage is high: {used_pct}% (Limit: {self.max_usage_percent}%)",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            severity=self.severity,
            message=f"Swap usage is healthy: {used_pct if used_pct is not None else 0.0}%",
        )


class NetworkSecurityPolicy(Policy):
    """
    Audits active network interfaces and status.
    """

    name = "Network Interface Status"
    description = "Checks active network interfaces and connectivity."
    severity = "LOW"

    def evaluate(self, inventory: Dict[str, Any]) -> PolicyResult:
        net_data = inventory.get("network", {})
        interfaces = net_data.get("interfaces", [])

        up_interfaces = [
            str(iface.get("interface") or iface.get("name") or "")
            for iface in interfaces
            if (iface.get("is_up") if isinstance(iface, dict) else getattr(iface, "is_up", False))
            and (iface.get("interface") or iface.get("name"))
        ]

        if not up_interfaces:
            return PolicyResult(
                policy_name=self.name,
                passed=False,
                severity="HIGH",
                message="No active network interfaces found.",
            )

        return PolicyResult(
            policy_name=self.name,
            passed=True,
            severity=self.severity,
            message=f"Active network interfaces: {', '.join(up_interfaces)}",
        )

