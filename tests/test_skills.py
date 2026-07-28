"""
Unit tests for ITAT Specialized Skills framework.
"""

from itat.skills.base import BaseSkill, SkillResult, SkillStatus
from itat.skills.manager import SkillManager


class DummySkill(BaseSkill):
    name = "dummy"
    description = "Dummy test skill"
    version = "1.0.0"
    target_service = "dummy_service"

    def check_health(self) -> SkillResult:
        return SkillResult(
            status=SkillStatus.OK,
            message="Dummy service is healthy",
            details={"version": "1.0"},
        )

    def analyze_logs(self, log_path=None, lines=100) -> SkillResult:
        return SkillResult(
            status=SkillStatus.OK,
            message="No errors in dummy log",
        )

    def auto_fix(self) -> SkillResult:
        return SkillResult(
            status=SkillStatus.OK,
            message="Dummy auto-fix complete",
            actions_taken=["Restarted dummy service"],
        )


def test_base_skill_and_manager():
    manager = SkillManager()
    skill = DummySkill()
    manager.register(skill)

    # Test list skills
    skill_list = manager.list_skills()
    assert len(skill_list) == 1
    assert skill_list[0]["name"] == "dummy"

    # Test health check
    health_res = manager.run_health_checks("dummy")
    assert "dummy" in health_res
    assert health_res["dummy"].status == SkillStatus.OK
    assert health_res["dummy"].is_healthy() is True

    # Test log analysis
    log_res = manager.run_log_analysis("dummy")
    assert log_res["dummy"].status == SkillStatus.OK

    # Test auto-fix
    fix_res = manager.run_auto_fix("dummy")
    assert fix_res.status == SkillStatus.OK
    assert "Restarted dummy service" in fix_res.actions_taken


from itat.skills.mysql import MySQLSkill
from itat.skills.powerbi import PowerBISkill


def test_mysql_and_powerbi_skills():
    mysql = MySQLSkill()
    assert mysql.name == "mysql"
    assert mysql.target_service == "mysql"
    health_mysql = mysql.check_health()
    assert health_mysql.status in (SkillStatus.OK, SkillStatus.WARNING, SkillStatus.CRITICAL)

    powerbi = PowerBISkill()
    assert powerbi.name == "powerbi"
    health_pbi = powerbi.check_health()
    assert health_pbi.status in (SkillStatus.OK, SkillStatus.WARNING, SkillStatus.ERROR)


if __name__ == "__main__":
    test_base_skill_and_manager()
    test_mysql_and_powerbi_skills()
    print("All skill unit tests passed!")
