"""
Skill Manager for loading, listing, and executing ITAT skills.
"""

from typing import Dict, List, Optional
from .base import BaseSkill, SkillResult, SkillStatus


class SkillManager:
    """
    Registry and execution engine for ITAT Support Skills.
    """

    def __init__(self):
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        """Register a new skill instance."""
        if not isinstance(skill, BaseSkill):
            raise TypeError(f"Expected BaseSkill subclass instance, got {type(skill)}")
        self._skills[skill.name] = skill

    def get_skill(self, name: str) -> Optional[BaseSkill]:
        """Get a skill by its registered name."""
        return self._skills.get(name)

    def list_skills(self) -> List[Dict[str, str]]:
        """List metadata for all registered skills."""
        return [skill.get_info() for skill in self._skills.values()]

    def run_health_checks(self, skill_name: Optional[str] = None) -> Dict[str, SkillResult]:
        """Run health checks for a specific skill or all registered skills."""
        results: Dict[str, SkillResult] = {}
        target_skills = (
            {skill_name: self._skills[skill_name]}
            if skill_name and skill_name in self._skills
            else self._skills
        )

        for name, skill in target_skills.items():
            try:
                results[name] = skill.check_health()
            except Exception as e:
                results[name] = SkillResult(
                    status=SkillStatus.CRITICAL,
                    message=f"Skill execution failed with error: {str(e)}",
                )
        return results

    def run_log_analysis(
        self, skill_name: Optional[str] = None, log_path: Optional[str] = None, lines: int = 100
    ) -> Dict[str, SkillResult]:
        """Run log analysis for a specific skill or all skills."""
        results: Dict[str, SkillResult] = {}
        target_skills = (
            {skill_name: self._skills[skill_name]}
            if skill_name and skill_name in self._skills
            else self._skills
        )

        for name, skill in target_skills.items():
            try:
                results[name] = skill.analyze_logs(log_path=log_path, lines=lines)
            except Exception as e:
                results[name] = SkillResult(
                    status=SkillStatus.ERROR,
                    message=f"Log analysis failed: {str(e)}",
                )
        return results

    def run_auto_fix(self, skill_name: str) -> SkillResult:
        """Execute automated remediation for a specific skill."""
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Skill '{skill_name}' not found in registry.",
            )
        try:
            return skill.auto_fix()
        except Exception as e:
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"Auto-fix failed with exception: {str(e)}",
            )
