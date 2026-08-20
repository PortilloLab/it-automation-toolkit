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


@patch("subprocess.run")
@patch("socket.create_connection")
def test_powerbi_gateway_status_fails_closed_on_unknown(mock_socket, mock_subproc):
    """
    If systemctl status can't be determined (e.g. missing binary, no systemd,
    permission error), the gateway must be reported as NOT active rather than
    assumed healthy. Failing "open" here would mask a real outage.
    """
    mock_socket.return_value.__enter__.return_value = MagicMock()
    mock_subproc.side_effect = FileNotFoundError("systemctl: command not found")

    pbi = PowerBISkill()
    assert pbi._check_gateway_active() is False

    health = pbi.check_health()
    assert health.status != SkillStatus.OK
    assert health.details["gateway_active"] is False


from itat.skills.postgresql import PostgreSQLSkill
from itat.skills.docker import DockerSkill
from itat.utils.services import ServiceManager
from itat.utils.paths import ensure_export_path


@patch("subprocess.run")
@patch("socket.create_connection")
def test_postgresql_skill_mocked(mock_socket, mock_subproc):
    mock_subproc.return_value = MagicMock(returncode=0, stdout="active\n")
    mock_socket.return_value.__enter__.return_value = MagicMock()

    pg = PostgreSQLSkill()
    health = pg.check_health()
    assert health.status == SkillStatus.OK
    assert "postgresql server is active" in health.message.lower()


@patch("subprocess.run")
def test_docker_skill_mocked(mock_subproc):
    def side_effect(cmd, **kwargs):
        if "is-active" in cmd:
            return MagicMock(returncode=0, stdout="active\n")
        elif "ps" in cmd:
            return MagicMock(returncode=0, stdout="c1|web|Up 2 hours|running\nc2|db|Exited (0) 10 min ago|exited\n")
        return MagicMock(returncode=0, stdout="")

    mock_subproc.side_effect = side_effect

    docker_skill = DockerSkill()
    health = docker_skill.check_health()
    assert health.status == SkillStatus.WARNING
    assert health.details["running_containers"] == 1
    assert health.details["exited_containers"] == 1


def test_ensure_export_path():
    path1 = ensure_export_path("test_report.html")
    assert "exports" in path1
    assert path1.endswith("test_report.html")


from itat.skills.antivirus import AntivirusSkill


def test_antivirus_skill():
    av = AntivirusSkill()
    health = av.check_health()
    assert health.status in (SkillStatus.OK, SkillStatus.WARNING, SkillStatus.CRITICAL)
    assert av.name == "antivirus"


if __name__ == "__main__":
    test_base_skill_and_manager()
    test_mysql_skill_mocked()
    test_powerbi_skill_mocked()
    test_powerbi_gateway_status_fails_closed_on_unknown()
    test_webservice_skill()
    test_antivirus_skill()
    print("All skill unit tests passed!")
