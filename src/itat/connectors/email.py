"""
Email / SMTP Connector for ITAT Alerts and Executive Reports.

Dispatches email alerts and attachments (HTML executive reports) via standard SMTP/TLS.
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Any, Dict, Optional

from .base import BaseConnector


class EmailConnector(BaseConnector):
    """
    Connector for dispatching email notifications and executive reports via SMTP.
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        use_tls: bool = True,
        sender_email: Optional[str] = None,
        default_recipient: Optional[str] = None,
        timeout: int = 15,
    ):
        self.smtp_host = smtp_host or os.environ.get("ITAT_SMTP_HOST", "localhost")
        self.smtp_port = int(smtp_port or os.environ.get("ITAT_SMTP_PORT", 587))
        self.smtp_user = smtp_user or os.environ.get("ITAT_SMTP_USER", "")
        self.smtp_password = smtp_password or os.environ.get("ITAT_SMTP_PASS", "")
        self.use_tls = use_tls
        self.sender_email = sender_email or os.environ.get("ITAT_SMTP_SENDER", self.smtp_user or "itat@localhost")
        self.default_recipient = default_recipient or os.environ.get("ITAT_SMTP_RECIPIENT", "")
        self.timeout = timeout

    def is_configured(self) -> bool:
        """Check if minimum SMTP parameters are configured."""
        return bool(self.smtp_host and (self.default_recipient or self.sender_email))

    def test_connection(self) -> bool:
        """Verify connection and handshake with SMTP server."""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                return True
        except Exception:
            return False

    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send email payload matching BaseConnector contract.
        Expected keys: 'subject', 'body', optional 'recipient', 'attachment'.
        """
        subject = data.get("subject", "ITAT Notification")
        body = data.get("body", "")
        recipient = data.get("recipient") or self.default_recipient
        attachment = data.get("attachment")
        is_html = data.get("is_html", False)

        return self.send_email(
            subject=subject,
            body=body,
            recipient=recipient,
            attachment_path=attachment,
            is_html=is_html,
        )

    def send_email(
        self,
        subject: str,
        body: str,
        recipient: Optional[str] = None,
        attachment_path: Optional[str] = None,
        is_html: bool = False,
    ) -> bool:
        """
        Send an email message with optional HTML content and file attachment.
        """
        target_recipient = recipient or self.default_recipient
        if not target_recipient:
            print("[!] Email Connector Error: No recipient address provided.")
            return False

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = target_recipient
        msg["Subject"] = subject

        mime_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, mime_type, "utf-8"))

        if attachment_path and os.path.exists(attachment_path):
            try:
                with open(attachment_path, "rb") as f:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                filename = os.path.basename(attachment_path)
                part.add_header("Content-Disposition", f"attachment; filename=\"{filename}\"")
                msg.attach(part)
            except Exception as e:
                print(f"[!] Email Connector Warning: Could not attach file {attachment_path}: {e}")

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=self.timeout) as server:
                server.ehlo()
                if self.use_tls:
                    server.starttls()
                    server.ehlo()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                return True
        except Exception as e:
            print(f"[!] Email Connector Error: Failed sending email to {target_recipient}: {e}")
            return False

    def send_alert(
        self,
        title: str,
        text: str,
        severity: str = "INFO",
        recipient: Optional[str] = None,
        attachment_path: Optional[str] = None,
    ) -> bool:
        """
        Send a formatted HTML alert email with optional report attachment.
        """
        severity_colors = {
            "CRITICAL": "#ef4444",
            "HIGH": "#f97316",
            "WARNING": "#f59e0b",
            "INFO": "#38bdf8",
        }
        color = severity_colors.get(severity.upper(), "#38bdf8")
        subject = f"[{severity.upper()}] ITAT Alert: {title}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #f8fafc; color: #1e293b; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
                .header {{ background-color: {color}; color: #ffffff; padding: 16px 24px; font-size: 1.2rem; font-weight: bold; }}
                .content {{ padding: 24px; line-height: 1.6; white-space: pre-wrap; font-family: monospace; background: #f1f5f9; margin: 16px; border-radius: 6px; }}
                .footer {{ padding: 12px 24px; font-size: 0.8rem; color: #64748b; border-top: 1px solid #e2e8f0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">🚨 {title}</div>
                <div class="content">{text}</div>
                <div class="footer">Sent automatically by IT Automation Toolkit (ITAT)</div>
            </div>
        </body>
        </html>
        """

        return self.send_email(
            subject=subject,
            body=html_body,
            recipient=recipient,
            attachment_path=attachment_path,
            is_html=True,
        )
