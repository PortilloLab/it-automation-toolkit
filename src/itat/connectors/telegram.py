"""
Telegram Bot Connector for ITAT Alerts and Incident Notifications.

Sends instant formatted notifications and audit reports directly to a Telegram chat or group.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional

from .base import BaseConnector


class TelegramConnector(BaseConnector):
    """
    Connector for dispatching system alerts to Telegram via Bot API.
    """

    API_BASE = "https://api.telegram.org"

    def __init__(
        self,
        bot_token: Optional[str] = None,
        chat_id: Optional[str] = None,
        timeout: int = 10,
    ):
        self.bot_token = (bot_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")).strip()
        self.chat_id = (chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")).strip()
        self.timeout = timeout

    def is_configured(self) -> bool:
        """Check if both bot_token and chat_id are present."""
        return bool(self.bot_token and self.chat_id)

    def test_connection(self) -> bool:
        """Verify that the bot token is valid via getMe endpoint."""
        if not self.bot_token:
            return False

        url = f"{self.API_BASE}/bot{self.bot_token}/getMe"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ITAT-Toolkit/0.1.0"}, method="GET")
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("ok", False)
        except Exception:
            return False

    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send raw message payload to the configured Telegram chat.
        """
        if not self.is_configured():
            print("[!] Telegram Connector Error: Bot token or chat_id is missing.")
            return False

        url = f"{self.API_BASE}/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": data.get("text", ""),
            "parse_mode": data.get("parse_mode", "HTML"),
            "disable_web_page_preview": True,
        }

        try:
            body = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=body,
                headers={"Content-Type": "application/json", "User-Agent": "ITAT-Toolkit/0.1.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                return res_data.get("ok", False)
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            print(f"[!] Telegram HTTP Error ({e.code}): {err_body}")
            return False
        except Exception as e:
            print(f"[!] Telegram Request Error: {str(e)}")
            return False

    def send_alert(self, title: str, text: str, severity: str = "INFO") -> bool:
        """
        Send a high-visibility formatted alert with severity badge and emojis.
        """
        emoji_map = {
            "CRITICAL": "🔥 <b>[CRITICAL]</b>",
            "HIGH": "🚨 <b>[HIGH]</b>",
            "WARNING": "⚠️ <b>[WARNING]</b>",
            "INFO": "ℹ️ <b>[INFO]</b>",
        }
        badge = emoji_map.get(severity.upper(), "📢 <b>[ALERT]</b>")

        # Telegram HTML safe formatting
        escaped_title = title.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        escaped_text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        formatted_msg = (
            f"{badge} <b>{escaped_title}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"{escaped_text}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<i>Reported by IT Automation Toolkit (ITAT)</i>"
        )

        return self.send({"text": formatted_msg, "parse_mode": "HTML"})

