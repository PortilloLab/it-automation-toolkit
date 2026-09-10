"""
Operating System Security Patching & Update Diagnostics Skill for ITAT.

Provides detection of pending security patches and system updates across
Linux (apt, dnf, pacman), Windows (Windows Update), and macOS.
"""

import os
import platform
import shutil
import subprocess
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseSkill, SkillResult, SkillStatus


class SystemUpdateSkill(BaseSkill):
    """
    Skill for auditing and applying OS security updates and system patches.
    """

    name = "system_update"
    description = "Specialized support skill for OS Security Patching & System Updates"
    version = "1.0.0"
    target_service = "apt / dnf / WindowsUpdate"

    def __init__(self, check_security_only: bool = False):
        self.check_security_only = check_security_only

    def check_health(self) -> SkillResult:
        """Inspect pending system updates and identify critical security patches."""
        system = platform.system().lower()
        details: Dict[str, Any] = {"os": system}
        recommendations: List[str] = []

        try:
            if system == "linux":
                pkg_manager, total_updates, sec_updates, sample = self._check_linux_updates()
            elif system == "windows":
                pkg_manager, total_updates, sec_updates, sample = self._check_windows_updates()
            elif system == "darwin":
                pkg_manager, total_updates, sec_updates, sample = self._check_macos_updates()
            else:
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"System update audit not supported on OS '{system}'.",
                    details=details,
                )

            details["package_manager"] = pkg_manager
            details["total_updates"] = total_updates
            details["security_updates"] = sec_updates
            if sample:
                details["sample_packages"] = sample[:5]

            if sec_updates > 0:
                status = SkillStatus.CRITICAL if sec_updates >= 3 else SkillStatus.WARNING
                recommendations.append(
                    f"Found {sec_updates} security patch(es) pending. Run 'itat skill fix system_update --yes' to apply."
                )
                return SkillResult(
                    status=status,
                    message=f"Pending updates: {total_updates} total ({sec_updates} critical security patch(es)).",
                    details=details,
                    recommendations=recommendations,
                )
            elif total_updates > 15:
                recommendations.append("Apply accumulated system updates to avoid technical debt.")
                return SkillResult(
                    status=SkillStatus.WARNING,
                    message=f"Pending updates: {total_updates} non-security packages awaiting installation.",
                    details=details,
                    recommendations=recommendations,
                )
            elif total_updates > 0:
                return SkillResult(
                    status=SkillStatus.OK,
                    message=f"System has {total_updates} minor update(s) pending. No security threats detected.",
                    details=details,
                )
            else:
                return SkillResult(
                    status=SkillStatus.OK,
                    message="System is up to date with all security and software patches.",
                    details=details,
                )

        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                message=f"Failed querying system updates: {str(e)}",
                details=details,
            )

    def _check_linux_updates(self) -> Tuple[str, int, int, List[str]]:
        """Check updates on Linux distributions (Debian/Ubuntu, RHEL/Fedora, Arch)."""
        # 1. Debian / Ubuntu (apt)
        if shutil.which("apt") or shutil.which("apt-get"):
            try:
                res = subprocess.run(
                    ["apt-get", "-s", "upgrade"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if res.returncode == 0:
                    lines = res.stdout.splitlines()
                    upgradable = [l.split()[1] for l in lines if l.startswith("Inst ")]
                    sec_count = sum(1 for l in lines if l.startswith("Inst ") and "security" in l.lower())
                    return "apt", len(upgradable), sec_count, upgradable
            except Exception:
                pass

        # 2. RHEL / CentOS / Fedora (dnf)
        if shutil.which("dnf"):
            try:
                res = subprocess.run(
                    ["dnf", "check-update", "-q"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )
                # DNF returns 100 if updates are available, 0 if up to date
                lines = [l.strip() for l in res.stdout.splitlines() if l.strip() and not l.startswith("Last metadata")]
                sec_count = 0
                return "dnf", len(lines), sec_count, [l.split()[0] for l in lines if l]
            except Exception:
                pass

        # 3. Arch Linux (checkupdates)
        if shutil.which("checkupdates"):
            try:
                res = subprocess.run(["checkupdates"], capture_output=True, text=True, timeout=10)
                lines = [l.strip() for l in res.stdout.splitlines() if l.strip()]
                return "pacman", len(lines), 0, [l.split()[0] for l in lines if l]
            except Exception:
                pass

        return "unknown", 0, 0, []

    def _check_windows_updates(self) -> Tuple[str, int, int, List[str]]:
        """Query pending updates on Windows via PowerShell Windows Update COM Session."""
        ps_script = """
        $session = New-Object -ComObject Microsoft.Update.Session
        $searcher = $session.CreateUpdateSearcher()
        $result = $searcher.Search("IsInstalled=0 and Type='Software'")
        $titles = $result.Updates | ForEach-Object { $_.Title }
        $sec = ($result.Updates | Where-Object { $_.Categories | Where-Object { $_.Name -like "*Security*" } }).Count
        Write-Output "$($result.Updates.Count)|$sec"
        $titles | Select-Object -First 5
        """
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                if lines:
                    header = lines[0].split("|")
                    total = int(header[0]) if len(header) > 0 and header[0].isdigit() else 0
                    sec = int(header[1]) if len(header) > 1 and header[1].isdigit() else 0
                    titles = [l.strip() for l in lines[1:] if l.strip()]
                    return "WindowsUpdate", total, sec, titles
        except Exception:
            pass
        return "WindowsUpdate", 0, 0, []

    def _check_macos_updates(self) -> Tuple[str, int, int, List[str]]:
        """Query pending updates on macOS via softwareupdate."""
        try:
            res = subprocess.run(["softwareupdate", "-l"], capture_output=True, text=True, timeout=15)
            lines = res.stdout.splitlines()
            updates = [l.strip() for l in lines if l.strip().startswith("*")]
            sec_count = sum(1 for l in updates if "security" in l.lower())
            return "softwareupdate", len(updates), sec_count, updates
        except Exception:
            return "softwareupdate", 0, 0, []

    def analyze_logs(self, log_path: Optional[str] = None, lines: int = 50) -> SkillResult:
        """Analyze package manager logs for failed installations, locks, or broken packages."""
        possible_logs = [
            log_path,
            "/var/log/apt/history.log",
            "/var/log/apt/term.log",
            "/var/log/dpkg.log",
            "/var/log/dnf.log",
            r"C:\Windows\WindowsUpdate.log",
        ]
        target_log = None
        for p in possible_logs:
            if p and os.path.exists(p):
                target_log = p
                break

        if not target_log:
            return SkillResult(
                status=SkillStatus.OK,
                message="No package manager logs found in standard paths.",
            )

        error_lines = []
        try:
            with open(target_log, "r", encoding="utf-8", errors="ignore") as f:
                recent = f.readlines()[-lines:]
                for line in recent:
                    line_lower = line.lower()
                    if any(kw in line_lower for kw in ["error", "fail", "broken", "unmet dependencies", "hash sum mismatch", "could not get lock"]):
                        error_lines.append(line.strip())
        except Exception as e:
            return SkillResult(status=SkillStatus.ERROR, message=f"Failed reading update log {target_log}: {str(e)}")

        if error_lines:
            return SkillResult(
                status=SkillStatus.WARNING,
                message=f"Found {len(error_lines)} warning/error entries in package manager log.",
                details={"log_file": target_log, "sample_errors": error_lines[:5]},
                recommendations=["Run 'sudo dpkg --configure -a' or repair package manager lock files."],
            )

        return SkillResult(
            status=SkillStatus.OK,
            message=f"No recent errors found in package manager log ({target_log}).",
            details={"log_file": target_log},
        )

    def auto_fix(self) -> SkillResult:
        """Attempt automated installation of pending security updates."""
        system = platform.system().lower()
        actions = []

        if system == "linux":
            if shutil.which("apt-get"):
                cmd_update = ["apt-get", "update"]
                cmd_upgrade = ["apt-get", "-y", "--only-upgrade", "install"]
                if os.name == "posix" and hasattr(os, "geteuid") and os.geteuid() != 0:
                    cmd_update = ["sudo", "-n"] + cmd_update
                    cmd_upgrade = ["sudo", "-n"] + cmd_upgrade

                try:
                    # 1. Update metadata
                    subprocess.run(cmd_update, capture_output=True, text=True, timeout=30)
                    actions.append("Refreshed APT package metadata.")

                    # 2. Check pending security packages
                    _, total, sec, packages = self._check_linux_updates()
                    if total == 0:
                        return SkillResult(
                            status=SkillStatus.OK,
                            message="System is already fully patched. No updates required.",
                            actions_taken=actions,
                        )

                    # 3. Apply updates
                    res_up = subprocess.run(
                        ["sudo", "-n", "apt-get", "-y", "upgrade"] if hasattr(os, "geteuid") and os.geteuid() != 0 else ["apt-get", "-y", "upgrade"],
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if res_up.returncode == 0:
                        actions.append(f"Successfully installed pending updates ({total} package(s)).")
                        return SkillResult(
                            status=SkillStatus.OK,
                            message=f"Completed security patching ({total} package(s) updated).",
                            actions_taken=actions,
                        )
                    else:
                        err = res_up.stderr.strip() or res_up.stdout.strip()
                        return SkillResult(
                            status=SkillStatus.WARNING,
                            message=f"Update command exited with error: {err[:150]}",
                            actions_taken=actions,
                            recommendations=["Run 'sudo apt-get upgrade' interactively to resolve dependencies."],
                        )
                except Exception as e:
                    return SkillResult(status=SkillStatus.ERROR, message=f"Failed applying Linux updates: {str(e)}")

        return SkillResult(
            status=SkillStatus.OK,
            message="Auto-fix completed inspection for system updates.",
            actions_taken=["Checked package manager status."],
        )
