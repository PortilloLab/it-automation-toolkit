"""
Antivirus and Malware Protection Skill for ITAT framework.

Provides malware diagnostics, process inspection for miners/trojans,
and integration with native antivirus engines (ClamAV on Linux, Windows Defender on Windows).
"""

import os
import platform
import subprocess
from typing import Optional
import psutil
from .base import BaseSkill, SkillResult, SkillStatus


class AntivirusSkill(BaseSkill):
    """
    Skill for inspecting malware threats, suspicious temporary processes, and antivirus status.
    """

    name = "antivirus"
    description = "Malware inspection, miner detection, and Antivirus health diagnostics"
    version = "1.0.0"
    target_service = "clamav-daemon / WinDefend"

    def __init__(self, temp_scan: bool = True):
        self.temp_scan = temp_scan

    def check_health(self) -> SkillResult:
        """Inspect system for active antivirus engines and suspicious temporary processes."""
        system = platform.system().lower()
        details = {"os": system}
        recommendations = []
        suspicious_procs = self._scan_suspicious_processes()

        details["suspicious_processes_count"] = len(suspicious_procs)
        if suspicious_procs:
            details["suspicious_processes"] = suspicious_procs[:5]

        # Check native AV status
        av_active = False
        if system == "linux":
            try:
                res = subprocess.run(["systemctl", "is-active", "clamav-daemon"], capture_output=True, text=True, timeout=5)
                av_active = res.stdout.strip() == "active"
            except Exception:
                av_active = False
            details["clamav_active"] = av_active

        elif system == "windows":
            try:
                res = subprocess.run(["sc", "query", "WinDefend"], capture_output=True, text=True, timeout=5)
                av_active = "RUNNING" in res.stdout
            except Exception:
                av_active = False
            details["windows_defender_active"] = av_active

        if suspicious_procs:
            recommendations.append("Terminate suspicious processes running from temporary directories (/tmp, AppData/Temp).")
            return SkillResult(
                status=SkillStatus.CRITICAL,
                message=f"Detected {len(suspicious_procs)} suspicious process(es) running from temporary locations.",
                details=details,
                recommendations=recommendations,
            )

        if av_active:
            return SkillResult(
                status=SkillStatus.OK,
                message="Antivirus engine is active and no suspicious temporary processes detected.",
                details=details,
            )
        else:
            return SkillResult(
                status=SkillStatus.WARNING,
                message="No suspicious processes found, but native Antivirus daemon (ClamAV / Defender) status is unconfirmed.",
                details=details,
                recommendations=["Ensure Windows Defender or ClamAV daemon is active on the system."],
            )

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 50) -> SkillResult:
        """Analyze Antivirus log files (ClamAV or syslog malware entries)."""
        possible_logs = [log_path, "/var/log/clamav/clamav.log", "/var/log/clamav/freshclam.log"]
        target_log = None
        for p in possible_logs:
            if p and os.path.exists(p):
                target_log = p
                break

        detections = []
        if target_log:
            try:
                with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                    recent = f.readlines()[-lines:]
                    for line in recent:
                        if any(kw in line.lower() for kw in ["found", "infected", "virus", "threat", "denied"]):
                            detections.append(line.strip())
            except Exception as e:
                return SkillResult(status=SkillStatus.ERROR, message=f"Failed reading AV log: {e}")

        if detections:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(detections)} virus/malware detection entries in Antivirus log.",
                details={"log_file": target_log, "detections": detections[:5]},
            )

        return SkillResult(status=SkillStatus.OK, message="No recent virus detection entries found in AV logs.")

    def auto_fix(self) -> SkillResult:
        """Attempt remediation by terminating suspicious temporary processes or triggering AV scan."""
        suspicious = self._scan_suspicious_processes()
        actions = []

        for proc_info in suspicious:
            try:
                pid = proc_info["pid"]
                p = psutil.Process(pid)
                p.kill()
                actions.append(f"Killed suspicious process PID {pid} ('{proc_info['name']}') running from '{proc_info['exe']}'")
            except Exception as e:
                actions.append(f"Failed to kill PID {proc_info['pid']}: {e}")

        if actions:
            return SkillResult(
                status=SkillStatus.OK,
                message=f"Remediated {len(actions)} suspicious process(es).",
                actions_taken=actions,
            )

        return SkillResult(
            status=SkillStatus.OK,
            message="No active suspicious processes found to terminate.",
            actions_taken=["Scanned process list; clean."],
        )

    def _scan_suspicious_processes(self) -> list:
        """Scan running processes for executables running inside temporary or cache directories."""
        suspicious = []
        temp_dirs = ["/tmp", "/var/tmp", "/dev/shm", "\\appdata\\local\\temp", "\\temp"]

        for proc in psutil.process_iter(["pid", "name", "exe", "cpu_percent"]):
            try:
                exe = proc.info.get("exe") or ""
                exe_lower = exe.lower()
                if any(td in exe_lower for td in temp_dirs):
                    suspicious.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "exe": exe,
                        "cpu": proc.info.get("cpu_percent", 0.0),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return suspicious
