"""
Tests for ConfigManager, ClientProfile, and dynamic policy configuration.
"""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from itat.core.config import ConfigManager, ClientProfile, AuditConfig, AlertConfig
from itat.policies import (
    PolicyEngine,
    DiskSpacePolicy,
    MemoryUsagePolicy,
    SwapUsagePolicy,
)
from itat.commands.audit import AuditCommand


class TestConfigManager:

    def test_default_profile(self):
        profile = ConfigManager.get_default_profile()
        assert profile.client_name == "Default Client"
        assert profile.environment == "Production"
        assert profile.audit.disk_max_percent == 85.0
        assert profile.audit.memory_max_percent == 85.0
        assert profile.audit.swap_max_percent == 80.0
        assert profile.audit.require_standard_user is True
        assert profile.audit.require_network_active is True
        assert profile.alerts.webhook_url is None

    def test_load_config_nonexistent(self):
        profile = ConfigManager.load_config("/path/to/nonexistent/file.json")
        assert profile.client_name == "Default Client"
        assert profile.audit.disk_max_percent == 85.0

    def test_load_config_invalid_json(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            f.write("{ invalid json content ...")
            temp_path = f.name

        try:
            profile = ConfigManager.load_config(temp_path)
            assert profile.client_name == "Default Client"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_save_and_load_config(self):
        custom = ClientProfile(
            client_name="Acme Corp",
            environment="Staging",
            audit=AuditConfig(
                disk_max_percent=92.5,
                memory_max_percent=90.0,
                swap_max_percent=70.0,
                require_standard_user=False,
                require_network_active=False,
            ),
            alerts=AlertConfig(
                webhook_url="https://hooks.example.com/test",
                telegram_bot_token="123:ABC",
                telegram_chat_id="999",
                email_recipient="admin@acme.com",
                email_sender="alerts@acme.com",
            ),
        )

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            temp_path = f.name

        try:
            ConfigManager.save_config(custom, temp_path)
            loaded = ConfigManager.load_config(temp_path)

            assert loaded.client_name == "Acme Corp"
            assert loaded.environment == "Staging"
            assert loaded.audit.disk_max_percent == 92.5
            assert loaded.audit.memory_max_percent == 90.0
            assert loaded.audit.swap_max_percent == 70.0
            assert loaded.audit.require_standard_user is False
            assert loaded.audit.require_network_active is False
            assert loaded.alerts.webhook_url == "https://hooks.example.com/test"
            assert loaded.alerts.telegram_bot_token == "123:ABC"
            assert loaded.alerts.telegram_chat_id == "999"
            assert loaded.alerts.email_recipient == "admin@acme.com"
            assert loaded.alerts.email_sender == "alerts@acme.com"
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_load_bundled_configs(self):
        default_path = os.path.join("configs", "default.json")
        enterprise_path = os.path.join("configs", "client_enterprise.json")

        if os.path.exists(default_path):
            p1 = ConfigManager.load_config(default_path)
            assert p1.client_name == "Standard Infrastructure"

        if os.path.exists(enterprise_path):
            p2 = ConfigManager.load_config(enterprise_path)
            assert p2.client_name == "Corporación Alpha Enterprise"
            assert p2.audit.disk_max_percent == 90.0
            assert p2.audit.memory_max_percent == 92.0


class TestPolicyEngineFromConfig:

    def test_from_config_defaults(self):
        engine = PolicyEngine.from_config()
        assert len(engine.policies) == 5

    def test_from_config_custom_thresholds(self):
        audit_cfg = AuditConfig(
            disk_max_percent=95.0,
            memory_max_percent=91.0,
            swap_max_percent=60.0,
            require_standard_user=False,
            require_network_active=False,
        )
        engine = PolicyEngine.from_config(audit_cfg)
        assert len(engine.policies) == 3

        disk_pol = next(p for p in engine.policies if isinstance(p, DiskSpacePolicy))
        assert disk_pol.max_usage_percent == 95.0

        mem_pol = next(p for p in engine.policies if isinstance(p, MemoryUsagePolicy))
        assert mem_pol.max_usage_percent == 91.0

        swap_pol = next(p for p in engine.policies if isinstance(p, SwapUsagePolicy))
        assert swap_pol.max_usage_percent == 60.0


class TestAuditCommandConfigIntegration:

    @patch("itat.commands.audit.scan")
    def test_audit_run_with_config_and_no_alerts(self, mock_scan):
        mock_scan.return_value = {
            "system": MagicMock(hostname="test-host"),
            "cpu": {},
            "memory": {"used_percent": 50.0, "swap_percent": 10.0},
            "disk": {"partitions": [{"mountpoint": "/", "used_percent": 40.0}]},
            "network": {"interfaces": [{"name": "eth0", "is_up": True}]},
            "users": {"current_user": "standard_user"},
        }

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            json.dump({
                "client_name": "Test Client",
                "audit": {"disk_max_percent": 90.0}
            }, f)
            cfg_path = f.name

        try:
            cmd = AuditCommand()
            ret = cmd.run(["--config", cfg_path, "--no-alerts"])
            assert ret == 0
        finally:
            if os.path.exists(cfg_path):
                os.remove(cfg_path)

    @patch("itat.commands.audit.scan")
    @patch("itat.commands.audit.HTTPConnector")
    @patch("itat.commands.audit.TelegramConnector")
    @patch("itat.commands.audit.EmailConnector")
    def test_audit_alert_dispatch_from_profile(self, mock_email, mock_telegram, mock_http, mock_scan):
        mock_scan.return_value = {
            "system": MagicMock(hostname="test-host"),
            "cpu": {},
            "memory": {"used_percent": 50.0, "swap_percent": 10.0},
            "disk": {"partitions": [{"mountpoint": "/", "used_percent": 95.0}]},  # HIGH severity failure
            "network": {"interfaces": [{"name": "eth0", "is_up": True}]},
            "users": {"current_user": "standard_user"},
        }

        mock_http.return_value.send_alert.return_value = True
        mock_telegram.return_value.send_alert.return_value = True
        mock_email.return_value.send_alert.return_value = True

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".json") as f:
            json.dump({
                "client_name": "Test Client",
                "audit": {"disk_max_percent": 80.0},
                "alerts": {
                    "webhook_url": "https://hooks.example.com/alerts",
                    "telegram_bot_token": "token123",
                    "telegram_chat_id": "chat123",
                    "email_recipient": "soc@example.com"
                }
            }, f)
            cfg_path = f.name

        try:
            cmd = AuditCommand()
            ret = cmd.run(["--config", cfg_path])
            assert ret == 1  # 1 because memory is 99% > 80%

            mock_http.assert_called_once_with("https://hooks.example.com/alerts")
            mock_telegram.assert_called_once_with(bot_token="token123", chat_id="chat123")
            mock_email.assert_called_once()
        finally:
            if os.path.exists(cfg_path):
                os.remove(cfg_path)
