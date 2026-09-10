"""
Unit tests for ITAT Connectors (HTTP, SSH, Telegram, Email).
Uses mocks to run deterministically in CI environments without external network dependencies.
"""

from unittest.mock import patch, MagicMock
import io
import json
import tempfile
import os
import urllib.error

from itat.connectors.http import HTTPConnector
from itat.connectors.ssh import SSHConnector
from itat.connectors.telegram import TelegramConnector
from itat.connectors.email import EmailConnector


@patch("urllib.request.urlopen")
def test_telegram_connector_mocked(mock_urlopen):
    # Success response mock
    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"ok": True}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    tg = TelegramConnector(bot_token="123456:ABC-DEF", chat_id="-100987654")
    assert tg.is_configured() is True
    assert tg.test_connection() is True

    sent = tg.send_alert("Test Alert", "Detailed error message", severity="CRITICAL")
    assert sent is True

    # Failure scenario (HTTPError)
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.telegram.org", 400, "Bad Request", {}, io.BytesIO(b'{"ok": false, "description": "Chat not found"}')
    )
    sent_fail = tg.send_alert("Fail Alert", "Will fail", severity="HIGH")
    assert sent_fail is False


@patch("smtplib.SMTP")
def test_email_connector_mocked(mock_smtp_class):
    mock_server = MagicMock()
    mock_server.__enter__.return_value = mock_server
    mock_smtp_class.return_value = mock_server

    email_conn = EmailConnector(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_user="user@example.com",
        smtp_password="password123",
        use_tls=True,
        sender_email="alerts@example.com",
        default_recipient="admin@example.com",
    )

    assert email_conn.is_configured() is True
    assert email_conn.test_connection() is True

    # Test send alert with attachment
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        tmp.write(b"<h1>Report</h1>")
        tmp_path = tmp.name

    try:
        sent = email_conn.send_alert(
            title="System Audit Failed",
            text="High RAM usage detected",
            severity="HIGH",
            attachment_path=tmp_path,
        )
        assert sent is True
        assert mock_server.send_message.called
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@patch("itat.connectors.http.urlopen")
def test_http_connector_mocked(mock_urlopen):
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__.return_value = mock_resp
    mock_urlopen.return_value = mock_resp

    http_conn = HTTPConnector("https://hooks.slack.com/services/XXX/YYY/ZZZ")
    assert http_conn.test_connection() is True

    sent = http_conn.send_alert("Audit Alert", "All policies passed", severity="INFO")
    assert sent is True


@patch("subprocess.run")
def test_ssh_connector_mocked(mock_subproc):
    mock_subproc.return_value = MagicMock(returncode=0, stdout="pong\n", stderr="")

    ssh = SSHConnector(host="192.168.1.50", user="admin", port=2222)
    assert ssh.test_connection() is True

    code, out, err = ssh.execute_command("uptime")
    assert code == 0
    assert "pong" in out

    sent = ssh.send({"status": "ok"})
    assert sent is True


if __name__ == "__main__":
    test_telegram_connector_mocked()
    test_email_connector_mocked()
    test_http_connector_mocked()
    test_ssh_connector_mocked()
    print("All connector unit tests passed!")
