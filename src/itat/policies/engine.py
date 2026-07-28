"""
Policy Engine for auditing system compliance.
"""

from typing import Any, Dict, List
from .base import Policy, PolicyResult
from .rules import DiskSpacePolicy, MemoryUsagePolicy, UserSecurityPolicy


class PolicyEngine:
    """
    Evaluates a suite of policies against system state.
    """

    def __init__(self, policies: List[Policy] = None):
        self.policies = policies or [
            DiskSpacePolicy(),
            MemoryUsagePolicy(),
            UserSecurityPolicy(),
        ]

    def add_policy(self, policy: Policy) -> None:
        """
        Add a new custom policy to the engine.
        """
        self.policies.append(policy)

    def evaluate_all(self, inventory: Dict[str, Any]) -> List[PolicyResult]:
        """
        Run all registered policies against the inventory.
        """
        return [policy.evaluate(inventory) for policy in self.policies]
