"""
SSL/TLS Certificate Inspection & Renewal Support Skill for ITAT.

Provides diagnostics for certificate expiration, chain validation,
and automated renewal via certbot or web service reloads.
"""

import os
import ssl
import socket
import subprocess
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from .base import BaseSkill, SkillResult, SkillStatus
from itat.utils.services import ServiceManager


class SSLCertificateSkill(BaseSkill):
    """
    Skill for diagnosing SSL/TLS certificates expiration, validity, and renewal status.
    """

    name = "ssl_cert"
    description = "Specialized support skill for SSL/TLS Certificate Expiration & Health"
    version = "1.0.0"
    target_service = "certbot / web-ssl"

    def __init__(
        self,
        target_host: str = "127.0.0.1",
        target_port: int = 443,
        warn_days: int = 30,
        critical_days: int = 7,
    ):
        self.target_host = target_host
        self.target_port = target_port
        self.warn_days = warn_days
        self.critical_days = critical_days

    def check_health(self) -> SkillResult:
        """Inspect SSL/TLS certificate validity and days until expiration."""
        details: Dict[str, Any] = {
            "host": self.target_host,
            "port": self.target_port,
        }
        recommendations = []

        try:
            context = ssl.create_default_context()
            # Do not fail on self-signed or hostname mismatches during diagnostics
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.target_host, self.target_port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.target_host) as ssock:
                    cert_bin = ssock.getpeercert(binary_form=True)
                    if not cert_bin:
                        return SkillResult(
                            status=SkillStatus.WARNING,
                            message=f"Connected to {self.target_host}:{self.target_port}, but no peer certificate presented.",
                            details=details,
                        )

                    # Decode expiration using DER format parser
                    cert_dict = ssock.getpeercert()

            if not cert_dict or "notAfter" not in cert_dict:
                # With CERT_NONE, getpeercert() without binary_form returns empty dict.
                # Re-check with standard verification or custom parser
                cert_info = self._get_cert_details(self.target_host, self.target_port)
            else:
                cert_info = cert_dict

            not_after_str = cert_info.get("notAfter")
            if not not_after_str:
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"Could not parse certificate expiration date for {self.target_host}.",
                    details=details,
                )

            # Date format: 'May 10 23:59:59 2026 GMT'
            exp_date = datetime.strptime(not_after_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            days_remaining = (exp_date - now).days

            details["expiration_date"] = exp_date.isoformat()
            details["days_remaining"] = days_remaining
            subject = cert_info.get("subject", ())
            common_names = [val[0][1] for val in subject if val and val[0][0] == "commonName"]
            details["common_name"] = common_names[0] if common_names else self.target_host

            if days_remaining < 0:
                recommendations.append(f"Certificate expired {abs(days_remaining)} day(s) ago! Renew immediately via 'itat skill fix ssl_cert' or 'certbot renew'.")
                return SkillResult(
                    status=SkillStatus.CRITICAL,
                    message=f"SSL Certificate for '{self.target_host}' has EXPIRED ({abs(days_remaining)} days ago)!",
                    details=details,
                    recommendations=recommendations,
                )
            elif days_remaining <= self.critical_days:
                recommendations.append(f"Certificate expires in {days_remaining} day(s)! Run 'itat skill fix ssl_cert' immediately.")
                return SkillResult(
                    status=SkillStatus.CRITICAL,
                    message=f"SSL Certificate for '{self.target_host}' is CRITICAL: expires in {days_remaining} days.",
                    details=details,
                    recommendations=recommendations,
                )
            elif days_remaining <= self.warn_days:
                recommendations.append(f"Certificate expires in {days_remaining} days. Schedule renewal before expiration.")
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"SSL Certificate for '{self.target_host}' expires soon ({days_remaining} days remaining).",
                    details=details,
                    recommendations=recommendations,
                )
            else:
                return SkillResult(
                    status=SkillStatus.OK,
                    message=f"SSL Certificate for '{self.target_host}' is healthy ({days_remaining} days remaining).",
                    details=details,
                )

        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            details["error"] = str(e)
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Unable to connect to SSL endpoint {self.target_host}:{self.target_port}: {str(e)}",
                details=details,
                recommendations=["Verify that the web server or HTTPS service is active and listening on port 443."],
            )

    def _get_cert_details(self, host: str, port: int) -> Dict[str, Any]:
        """Fetch certificate with verification enabled or fallback to OpenSSL CLI."""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    return ssock.getpeercert() or {}
        except Exception:
            # Fallback using openssl command line if available
            try:
                cmd = ["openssl", "s_client", "-connect", f"{host}:{port}", "-servername", host]
                proc = subprocess.run(cmd, input="", text=True, capture_output=True, timeout=5)
                # Parse x509 enddate
                x509_cmd = ["openssl", "x509", "-noout", "-enddate", "-subject"]
                proc_x509 = subprocess.run(x509_cmd, input=proc.stdout, text=True, capture_output=True, timeout=5)
                out = proc_x509.stdout
                res = {}
                for line in out.splitlines():
                    if line.startswith("notAfter="):
                        res["notAfter"] = line.split("=", 1)[1].strip()
                    elif line.startswith("subject="):
                        res["subject"] = [(( "commonName", line.split("CN =", 1)[1].split("/")[0].strip() ),)]
                return res
            except Exception:
                return {}

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 50) -> SkillResult:
        """Analyze Certbot or web server SSL log entries."""
        possible_logs = [
            log_path,
            "/var/log/letsencrypt/letsencrypt.log",
            "/var/log/nginx/error.log",
            "/var/log/apache2/error.log",
        ]
        target_log = None
        for p in possible_logs:
            if p and os.path.exists(p):
                target_log = p
                break

        if not target_log:
            return SkillResult(
                status=SkillStatus.OK,
                message="No Let's Encrypt or Web Server SSL log files found in default locations.",
            )

        error_lines = []
        try:
            with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                recent = f.readlines()[-lines:]
                for line in recent:
                    if any(kw in line.lower() for kw in ["cert", "ssl", "handshake", "expired", "failed", "unauthorized"]):
                        error_lines.append(line.strip())
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Failed reading SSL log {target_log}: {str(e)}",
            )

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} SSL/Certificate related log entries in {target_log}.",
                details={"log_file": target_log, "sample_errors": error_lines[:5]},
                recommendations=["Verify DNS records, firewall HTTP-01 challenge rules, or rate limits."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message=f"No recent SSL errors found in {target_log}.",
            details={"log_file": target_log},
        )

    def auto_fix(self) -> SkillResult:
        """Attempt automated certificate renewal via certbot or web server reload."""
        actions = []

        # 1. Attempt certbot renew
        try:
            cmd = ["certbot", "renew", "--non-interactive", "--no-random-sleep-on-renew"]
            if os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() != 0:
                cmd = ["sudo", "-n"] + cmd

            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if proc.returncode == 0:
                actions.append("Successfully executed 'certbot renew'.")
                # Reload nginx or apache if running
                if ServiceManager.is_service_active("nginx"):
                    ServiceManager.restart_service("nginx")
                    actions.append("Reloaded Nginx web server.")
                elif ServiceManager.is_service_active("apache2"):
                    ServiceManager.restart_service("apache2")
                    actions.append("Reloaded Apache web server.")

                return SkillResult(
                    status=SkillStatus.OK,
                    message="SSL certificate renewal completed successfully.",
                    actions_taken=actions,
                )
            else:
                err = proc.stderr.strip() or proc.stdout.strip()
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"Certbot renewal attempted but exited with: {err[:150]}",
                    actions_taken=[f"Certbot command failed: {err[:100]}"],
                    recommendations=["Run 'sudo certbot renew' manually to review interactive challenge prompts."],
                )
        except FileNotFoundError:
            # Certbot binary not present
            return SkillResult(
                status=SkillStatus.WARNING,
                message="'certbot' utility is not installed on this system.",
                recommendations=["Install certbot ('apt install certbot python3-certbot-nginx') to enable automated renewal."],
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Exception during SSL auto-fix: {str(e)}",
            )
