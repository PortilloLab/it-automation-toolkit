"""
Base Skill interface and result structures.

Defines the contract for all client-specific support skills.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class SkillStatus(Enum):
    """Execution status for a skill diagnostic or action."""
    OK = "OK"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class SkillResult:
    """Standard result returned by skill checks and actions."""
    status: SkillStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    actions_taken: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def is_healthy(self) -> bool:
        return self.status == SkillStatus.OK


class BaseSkill(ABC):
    """
    Abstract Base Class for all ITAT Specialized Support Skills.
    
    A Skill provides domain-specific or application-specific diagnostic,
    log analysis, and automated remediation capabilities for client software.
    """

    name: str = "base_skill"
    description: str = "Base skill interface"
    version: str = "1.0.0"
    target_service: str = "generic"

    @abstractmethod
    def check_health(self) -> SkillResult:
        """
        Check health and status of the target software/service.
        """
        pass

    @abstractmethod
    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 100) -> SkillResult:
        """
        Analyze application logs for errors or suspicious patterns.
        """
        pass

    @abstractmethod
    def auto_fix(self) -> SkillResult:
        """
        Attempt automated remediation for known issue conditions.
        """
        pass

    def get_info(self) -> Dict[str, str]:
        """Return metadata about this skill."""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "target_service": self.target_service,
        }
