"""
Policy Engine for auditing system compliance.
"""

from typing import Any, Dict, List, Optional
from itat.core.serialization import to_dict
from .base import Policy, PolicyResult
from .rules import DiskSpacePolicy, MemoryUsagePolicy, UserSecurityPolicy, SwapUsagePolicy, NetworkSecurityPolicy


class PolicyEngine:
    """
    Evaluates a suite of policies against system state.
    """

    def __init__(self, policies: List[Policy] = None):
        self.policies = policies or [
            DiskSpacePolicy(),
            MemoryUsagePolicy(),
            SwapUsagePolicy(),
            UserSecurityPolicy(),
            NetworkSecurityPolicy(),
        ]

    @classmethod
    def from_config(cls, config: Optional[Any] = None) -> "PolicyEngine":
        """
        Factory method to instantiate PolicyEngine using an AuditConfig profile.
        """
        if not config:
            return cls()

        policies = [
            DiskSpacePolicy(max_usage_percent=getattr(config, "disk_max_percent", 85.0)),
            MemoryUsagePolicy(max_usage_percent=getattr(config, "memory_max_percent", 85.0)),
            SwapUsagePolicy(max_usage_percent=getattr(config, "swap_max_percent", 80.0)),
        ]
        if getattr(config, "require_standard_user", True):
            policies.append(UserSecurityPolicy())
        if getattr(config, "require_network_active", True):
            policies.append(NetworkSecurityPolicy())

        return cls(policies=policies)

    def add_policy(self, policy: Policy) -> None:
        """
        Add a new custom policy to the engine.
        """
        self.policies.append(policy)

    def evaluate_all(self, inventory: Any) -> List[PolicyResult]:
        """
        Run all registered policies against the normalized inventory.
        """
        normalized_data = to_dict(inventory)
        return [policy.evaluate(normalized_data) for policy in self.policies]
