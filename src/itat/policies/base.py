"""
Base Policy definition.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PolicyResult:
    """
    Result of a policy evaluation.
    """

    policy_name: str
    passed: bool
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    message: str


class Policy(ABC):
    """
    Abstract base class for system audit and security policies.
    """

    name: str = ""
    description: str = ""
    severity: str = "MEDIUM"

    @abstractmethod
    def evaluate(self, inventory: Dict[str, Any]) -> PolicyResult:
        """
        Evaluate the policy against system inventory data.
        """
        raise NotImplementedError
