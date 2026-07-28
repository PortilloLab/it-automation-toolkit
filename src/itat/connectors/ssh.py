"""
SSH Connector.

Executes remote commands and transfers inventory reports over SSH.
"""

import json
import subprocess
from typing import Any, Dict, Optional, Tuple

from .base import BaseConnector


class SSHConnector(BaseConnector):
    """
    Connector for managing remote Linux servers over SSH.
    """

    def __init__(self, host: str, user: str = "root", port: int = 22, key_file: Optional[str] = None):
        self.host = host
        self.user = user
        self.port = port
        self.key_file = key_file

    def _build_ssh_cmd(self, remote_cmd: str) -> list[str]:
        cmd = [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "ConnectTimeout=5",
            "-p", str(self.port),
        ]
        if self.key_file:
            cmd.extend(["-i", self.key_file])
        cmd.append(f"{self.user}@{self.host}")
        cmd.append(remote_cmd)
        return cmd

    def test_connection(self) -> bool:
        """
        Test SSH connection to remote host.
        """
        try:
            cmd = self._build_ssh_cmd("echo ping")
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=6)
            return res.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False

    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a shell command on the remote server.

        Returns (return_code, stdout, stderr).
        """
        try:
            cmd = self._build_ssh_cmd(command)
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30)
            return res.returncode, res.stdout, res.stderr
        except Exception as e:
            return 1, "", str(e)

    def send(self, data: Dict[str, Any]) -> bool:
        """
        Send inventory JSON data to remote host via SSH stdin.
        """
        json_str = json.dumps(data, ensure_ascii=False)
        remote_cmd = "cat > /tmp/itat_inventory.json"
        try:
            cmd = self._build_ssh_cmd(remote_cmd)
            res = subprocess.run(cmd, input=json_str, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            return res.returncode == 0
        except Exception as e:
            print(f"[!] SSH Send Error: {e}")
            return False
