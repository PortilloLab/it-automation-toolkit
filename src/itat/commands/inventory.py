"""
Inventory command.
"""

from itat.core.command import Command
from itat.inventory.scanner import scan
from itat.inventory.export import export_json, export_markdown


class InventoryCommand(Command):
    """
    Inventory command.
    """

    name = "inventory"
    description = "Collect system inventory."

    def run(self, args: list[str]) -> int:

        inventory = scan()

        system = inventory["system"]
        cpu = inventory["cpu"]
        memory = inventory["memory"]
        disk = inventory["disk"]
        network = inventory["network"]

        # Parse export arguments
        if "--json" in args:
            idx = args.index("--json")
            if idx + 1 < len(args):
                out_path = args[idx + 1]
                export_json(inventory, out_path)
                print(f"[+] Inventory exported to JSON: {out_path}")

        if "--markdown" in args or "-m" in args:
            flag = "--markdown" if "--markdown" in args else "-m"
            idx = args.index(flag)
            if idx + 1 < len(args):
                out_path = args[idx + 1]
                export_markdown(inventory, out_path)
                print(f"[+] Inventory exported to Markdown: {out_path}")

        print("=" * 60)
        print("IT Automation Toolkit - Inventory")
        print("=" * 60)

        print("\nSYSTEM")
        print("-" * 60)
        print(f"Hostname        : {system.hostname}")
        print(f"Operating System: {system.operating_system}")
        print(f"Kernel          : {system.kernel}")
        print(f"Architecture    : {system.architecture}")
        print(f"Python          : {system.python_version}")
        print(f"User            : {system.current_user}")

        print("\nCPU")
        print("-" * 60)
        print(f"Processor       : {cpu.processor}")
        print(f"Architecture    : {cpu.architecture}")
        print(f"Physical Cores  : {cpu.physical_cores}")
        print(f"Logical Cores   : {cpu.logical_cores}")
        print(f"Frequency       : {cpu.current_frequency} MHz")

        print("\nMEMORY (RAM)")
        print("-" * 60)
        print(f"Total RAM       : {memory.total_gb} GB")
        print(f"Used RAM        : {memory.used_gb} GB ({memory.used_percent}%)")
        print(f"Available RAM   : {memory.available_gb} GB")
        print(f"Total Swap      : {memory.swap_total_gb} GB")
        print(f"Used Swap       : {memory.swap_used_gb} GB ({memory.swap_percent}%)")

        print("\nDISKS")
        print("-" * 60)
        for part in disk.partitions:
            print(f"Device: {part.device} ({part.fstype}) -> {part.mountpoint}")
            print(f"  Usage: {part.used_gb} GB / {part.total_gb} GB ({part.used_percent}%) | Free: {part.free_gb} GB")

        print("\nNETWORK INTERFACES")
        print("-" * 60)
        for net in network.interfaces:
            status = "UP" if net.is_up else "DOWN"
            print(f"Interface: {net.interface} [{status}]")
            print(f"  IP Address : {net.ip_address}")
            print(f"  MAC Address: {net.mac_address}")

        processes = inventory.get("processes", [])
        print("\nTOP PROCESSES (By Memory Usage)")
        print("-" * 60)
        for p in processes:
            print(f"PID: {p.pid:<7} User: {p.username:<10} RAM: {p.memory_percent:<5}% CPU: {p.cpu_percent:<5}% Command: {p.name}")

        return 0