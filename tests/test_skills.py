"""
Unit tests for ITAT Specialized Skills framework.
Includes mocks for subprocess and socket to run deterministically in CI environments.
"""

from unittest.mock import patch, MagicMock
import socket
from itat.skills.base import BaseSkill, SkillResult, SkillStatus
from itat.skills.manager import SkillManager
from itat.skills.mysql import MySQLSkill
from itat.skills.powerbi import PowerBISkill
from itat.skills.builtin import WebServiceSkill


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

    skill_list = manager.list_skills()
    assert len(skill_list) == 1
    assert skill_list[0]["name"] == "dummy"

    health_res = manager.run_health_checks("dummy")
    assert "dummy" in health_res
    assert health_res["dummy"].status == SkillStatus.OK
    assert health_res["dummy"].is_healthy() is True

    log_res = manager.run_log_analysis("dummy")
    assert log_res["dummy"].status == SkillStatus.OK

    fix_res = manager.run_auto_fix("dummy")
    assert fix_res.status == SkillStatus.OK
    assert "Restarted dummy service" in fix_res.actions_taken


@patch("subprocess.run")
@patch("socket.create_connection")
def test_mysql_skill_mocked(mock_socket, mock_subproc):
    mock_subproc.return_value = MagicMock(returncode=0, stdout="active\n")
    mock_socket.return_value.__enter__.return_value = MagicMock()

    mysql = MySQLSkill()
    health = mysql.check_health()
    assert health.status == SkillStatus.OK
    assert "active" in health.message.lower()

    mock_subproc.return_value = MagicMock(returncode=1, stdout="inactive\n")
    health_fail = mysql.check_health()
    assert health_fail.status == SkillStatus.CRITICAL


@patch("subprocess.run")
@patch("socket.create_connection")
def test_powerbi_skill_mocked(mock_socket, mock_subproc):
    mock_socket.return_value.__enter__.return_value = MagicMock()
    mock_subproc.return_value = MagicMock(returncode=0, stdout="active\n")

    pbi = PowerBISkill()
    health = pbi.check_health()
    assert health.status == SkillStatus.OK

    # Mock cloud connectivity timeout (socket.timeout)
    mock_socket.side_effect = socket.timeout("Connection timeout")
    health_no_cloud = pbi.check_health()
    assert health_no_cloud.status == SkillStatus.ERROR


def test_webservice_skill():
    web = WebServiceSkill(service_name="nginx")
    assert web.name == "nginx"
    assert web.target_service == "nginx"


if __name__ == "__main__":
    test_base_skill_and_manager()
    test_mysql_skill_mocked()
    test_powerbi_skill_mocked()
    test_webservice_skill()
    print("All skill unit tests passed!")
