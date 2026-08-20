"""
HTTP / REST API Connector.

Sends inventory reports and system metrics to a remote API or Webhook.
"""

import json
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from typing import Any, Dict, Optional

from .base import BaseConnector


class HTTPConnector(BaseConnector):
    """
    Connector for sending data over HTTP/HTTPS REST APIs.
    """

    def __init__(self, endpoint_url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 10):
        self.endpoint_url = endpoint_url
        self.timeout = timeout
        self.headers = headers or {"Content-Type": "application/json", "User-Agent": "ITAT-Toolkit/0.1.0"}

    def test_connection(self) -> bool:
        """
        Check if the endpoint is reachable with a HEAD/GET request.
        """
        try:
            req = Request(self.endpoint_url, headers=self.headers, method="GET")
            with urlopen(req, timeout=self.timeout) as response:
                return response.status in (200, 201, 202, 204)
        except (URLError, HTTPError, OSError):
            return False

    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send JSON payload to the configured endpoint via HTTP POST.
        """
        try:
            payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
            req = Request(self.endpoint_url, data=payload, headers=self.headers, method="POST")

            with urlopen(req, timeout=self.timeout) as response:
                return response.status in (200, 201, 202, 204)
        except (URLError, HTTPError, OSError) as e:
            print(f"[!] HTTP Connector Error: {e}")
            return False

    def send_alert(self, title: str, text: str, severity: str = "INFO") -> bool:
        """
        Send formatted alert message over Webhook (supports Slack, Discord, and REST endpoints).
        """
        url_lower = self.endpoint_url.lower()

        if "slack.com" in url_lower:
            payload = {"text": f"🚨 *{title}* [{severity}]\n{text}"}
        elif "discord.com" in url_lower:
            payload = {"content": f"🚨 **{title}** [{severity}]\n{text}"}
        else:
            payload = {
                "event": "ITAT_ALERT",
                "title": title,
                "text": text,
                "severity": severity,
            }

        return self.send(payload)
