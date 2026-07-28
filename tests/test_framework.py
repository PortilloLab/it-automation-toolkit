"""
Unit test suite for IT Automation Toolkit.
"""

from itat.core.registry import CommandRegistry
from itat.commands.inventory import InventoryCommand
from itat.commands.doctor import DoctorCommand
from itat.commands.audit import AuditCommand
from itat.commands.version import VersionCommand
from itat.inventory.scanner import scan
from itat.policies import PolicyEngine, DiskSpacePolicy, MemoryUsagePolicy, UserSecurityPolicy


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
