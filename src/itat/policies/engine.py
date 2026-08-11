"""
Policy Engine for auditing system compliance.
"""

from typing import Any, Dict, List
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
