"""
Unit test suite for IT Automation Toolkit.
"""

import html
import os
import tempfile
from itat.core.registry import CommandRegistry
from itat.commands.inventory import InventoryCommand
from itat.commands.doctor import DoctorCommand
from itat.commands.audit import AuditCommand
from itat.commands.version import VersionCommand
from itat.inventory.scanner import scan
from itat.policies import PolicyEngine, DiskSpacePolicy, MemoryUsagePolicy, UserSecurityPolicy
from itat.reports.html import generate_html_report


def test_command_registry():
    registry = CommandRegistry()
    cmd = InventoryCommand()
    registry.register(cmd)

    assert registry.get("inventory") == cmd
    assert "inventory" in registry.list_all()


def test_inventory_scanner():
    inventory = scan()
    assert "system" in inventory
    assert "cpu" in inventory
    assert "memory" in inventory
    assert "disk" in inventory
    assert "network" in inventory
    assert "processes" in inventory


def test_policy_engine():
    inventory = scan()
    engine = PolicyEngine([
        DiskSpacePolicy(max_usage_percent=99.0),
        MemoryUsagePolicy(max_usage_percent=99.0),
        UserSecurityPolicy(),
    ])
    results = engine.evaluate_all(inventory)

    assert len(results) == 3
    for r in results:
        assert hasattr(r, "passed")
        assert hasattr(r, "severity")
        assert hasattr(r, "message")


def test_commands_instantiation():
    doc = DoctorCommand()
    aud = AuditCommand()
    ver = VersionCommand()

    assert doc.name == "doctor"
    assert aud.name == "audit"
    assert ver.name == "version"


def test_html_xss_protection():
    payload_1 = "<script>alert('XSS')</script>"
    payload_2 = "<img src=x onerror=alert(1)>"
    malicious_inventory = {
        "system": {
            "hostname": payload_1,
            "operating_system": payload_2,
            "kernel": "Linux",
            "architecture": "x86_64",
            "python_version": "3.11",
            "current_user": "user",
        },
        "disk": {"partitions": []},
        "network": {"interfaces": []},
    }
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        out_path = tmp.name

    try:
        generate_html_report(malicious_inventory, output_path=out_path)
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert payload_1 not in content
        assert html.escape(payload_1) in content
        assert payload_2 not in content
        assert html.escape(payload_2) in content
    finally:
        if os.path.exists(out_path):
            os.remove(out_path)


if __name__ == "__main__":
    test_command_registry()
    test_inventory_scanner()
    test_policy_engine()
    test_commands_instantiation()
    test_html_xss_protection()
    print("All framework unit tests passed!")
