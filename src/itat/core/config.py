"""
Configuration Manager and Client Profile definitions for ITAT.

Supports per-client threshold customization, multi-channel alert targets,
and environment-specific audit policies via JSON configuration files.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, Optional


@dataclass
class AuditConfig:
    """Configurable thresholds and options for system security audit policies."""
    disk_max_percent: float = 85.0
    memory_max_percent: float = 85.0
    swap_max_percent: float = 80.0
    require_standard_user: bool = True
    require_network_active: bool = True


@dataclass
class AlertConfig:
    """Notification targets and endpoint configurations for a client environment."""
    webhook_url: Optional[str] = None
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    email_recipient: Optional[str] = None
    email_sender: Optional[str] = None


@dataclass
class ClientProfile:
    """Full client configuration profile."""
    client_name: str = "Default Client"
    environment: str = "Production"
    audit: AuditConfig = field(default_factory=AuditConfig)
    alerts: AlertConfig = field(default_factory=AlertConfig)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ConfigManager:
    """
    Utility for loading, validating, and saving ITAT client profiles.
    """

    @staticmethod
    def get_default_profile() -> ClientProfile:
        """Return a fresh default client profile."""
        return ClientProfile()

    @classmethod
    def load_config(cls, file_path: str) -> ClientProfile:
        """
        Load and parse a client configuration profile from a JSON file.
        Falls back to default profile if file not found or invalid.
        """
        if not file_path or not os.path.exists(file_path):
            return cls.get_default_profile()

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            audit_data = data.get("audit", {})
            alerts_data = data.get("alerts", {})

            audit_cfg = AuditConfig(
                disk_max_percent=float(audit_data.get("disk_max_percent", 85.0)),
                memory_max_percent=float(audit_data.get("memory_max_percent", 85.0)),
                swap_max_percent=float(audit_data.get("swap_max_percent", 80.0)),
                require_standard_user=bool(audit_data.get("require_standard_user", True)),
                require_network_active=bool(audit_data.get("require_network_active", True)),
            )

            alert_cfg = AlertConfig(
                webhook_url=alerts_data.get("webhook_url"),
                telegram_bot_token=alerts_data.get("telegram_bot_token"),
                telegram_chat_id=alerts_data.get("telegram_chat_id"),
                email_recipient=alerts_data.get("email_recipient"),
                email_sender=alerts_data.get("email_sender"),
            )

            return ClientProfile(
                client_name=data.get("client_name", "Default Client"),
                environment=data.get("environment", "Production"),
                audit=audit_cfg,
                alerts=alert_cfg,
            )

        except Exception as e:
            print(f"[!] Warning: Failed parsing config file '{file_path}': {e}. Using defaults.")
            return cls.get_default_profile()

    @classmethod
    def save_config(cls, profile: ClientProfile, file_path: str) -> str:
        """
        Save a client profile to a JSON file.
        """
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        return file_path
