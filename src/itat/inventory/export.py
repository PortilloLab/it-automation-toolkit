"""
Inventory Exporter.

Export inventory data to JSON and Markdown formats.
Uses centralized core.serialization.to_dict for data normalization.
"""

import json
from typing import Any
from itat.core.serialization import to_dict


def export_json(inventory_data: dict, filepath: str) -> None:
    """
    Export inventory data to a JSON file.
    """
    clean_data = to_dict(inventory_data)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)


def export_markdown(inventory_data: dict, filepath: str) -> None:
    """
    Export inventory data to a Markdown report file.
    """
    clean_data = to_dict(inventory_data)
    sys = clean_data.get("system", {})
    cpu = clean_data.get("cpu", {})
    mem = clean_data.get("memory", {})
    disk = clean_data.get("disk", {})
    net = clean_data.get("network", {})
    users_info = clean_data.get("users", {})

    lines = []
    lines.append("# IT Automation Toolkit - System Inventory Report\n")

    lines.append("## System Details")
    lines.append(f"- **Hostname:** `{sys.get('hostname', 'N/A')}`")
    lines.append(f"- **Operating System:** {sys.get('operating_system', 'N/A')}")
    lines.append(f"- **Kernel:** {sys.get('kernel', 'N/A')}")
    lines.append(f"- **Architecture:** {sys.get('architecture', 'N/A')}")
    lines.append(f"- **Python Version:** {sys.get('python_version', 'N/A')}")
    lines.append(f"- **Active User:** {sys.get('current_user', 'N/A')}\n")

    # Active user sessions
    if users_info.get("active_users"):
        lines.append("## Active User Sessions")
        lines.append(f"Total Active Sessions: {users_info.get('total_active_sessions', 0)}")
        lines.append("| Username | Terminal | Host |")
        lines.append("| --- | --- | --- |")
        for u in users_info.get("active_users", []):
            lines.append(f"| `{u.get('username')}` | `{u.get('terminal')}` | `{u.get('host')}` |")
        lines.append("")

    lines.append("## CPU Details")
    lines.append(f"- **Processor:** {cpu.get('processor', 'N/A')}")
    lines.append(f"- **Architecture:** {cpu.get('architecture', 'N/A')}")
    lines.append(f"- **Physical Cores:** {cpu.get('physical_cores', 0)}")
    lines.append(f"- **Logical Cores:** {cpu.get('logical_cores', 0)}")
    lines.append(f"- **Frequency:** {cpu.get('current_frequency', 0.0)} MHz\n")

    lines.append("## Memory (RAM)")
    lines.append(f"- **Total RAM:** {mem.get('total_gb', 0.0)} GB")
    lines.append(f"- **Used RAM:** {mem.get('used_gb', 0.0)} GB ({mem.get('used_percent', 0.0)}%)")
    lines.append(f"- **Available RAM:** {mem.get('available_gb', 0.0)} GB")
    lines.append(f"- **Total Swap:** {mem.get('swap_total_gb', 0.0)} GB")
    lines.append(f"- **Used Swap:** {mem.get('swap_used_gb', 0.0)} GB ({mem.get('swap_percent', 0.0)}%)\n")

    lines.append("## Disk Storage")
    lines.append("| Device | Mountpoint | Filesystem | Used | Total | Free | Usage % |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for part in disk.get("partitions", []):
        lines.append(
            f"| `{part.get('device')}` | `{part.get('mountpoint')}` | {part.get('fstype')} | "
            f"{part.get('used_gb')} GB | {part.get('total_gb')} GB | {part.get('free_gb')} GB | {part.get('used_percent')}% |"
        )
    lines.append("")

    lines.append("## Network Interfaces")
    lines.append("| Interface | Status | IP Address | MAC Address |")
    lines.append("| --- | --- | --- | --- |")
    for iface in net.get("interfaces", []):
        status = "UP" if iface.get("is_up") else "DOWN"
        lines.append(
            f"| `{iface.get('interface')}` | {status} | `{iface.get('ip_address')}` | `{iface.get('mac_address')}` |"
        )
    lines.append("")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
