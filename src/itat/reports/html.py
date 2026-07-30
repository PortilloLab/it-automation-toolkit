"""
HTML Report Generator.

Generates sleek, dark-themed HTML executive reports for inventory and policy audits.
Fully safe against HTML/XSS injection and integrated with i18n.
"""

import html
from typing import Any, Dict, List
from itat.core.serialization import to_dict
from itat.i18n import t


def generate_html_report(inventory_data: Dict[str, Any], audit_results: List[Any] = None, output_path: str = "report.html") -> str:
    """
    Generate an HTML report with dark mode glassmorphism UI.
    Uses html.escape to prevent XSS injection.
    """
    data = to_dict(inventory_data)
    sys = data.get("system", {})
    cpu = data.get("cpu", {})
    mem = data.get("memory", {})
    disk = data.get("disk", {})
    net = data.get("network", {})

    lang_code = t.lang

    # Disk rows
    disk_rows = ""
    for part in disk.get("partitions", []):
        pct = part.get("used_percent", 0)
        badge_class = "badge-danger" if pct > 85 else ("badge-warning" if pct > 70 else "badge-success")
        device_esc = html.escape(str(part.get('device', '')))
        mount_esc = html.escape(str(part.get('mountpoint', '')))
        fstype_esc = html.escape(str(part.get('fstype', '')))
        disk_rows += f"""
        <tr>
            <td><code>{device_esc}</code></td>
            <td><code>{mount_esc}</code></td>
            <td><span class="pill">{fstype_esc}</span></td>
            <td>{part.get('used_gb')} GB / {part.get('total_gb')} GB</td>
            <td>{part.get('free_gb')} GB</td>
            <td><span class="badge {badge_class}">{pct}%</span></td>
        </tr>
        """

    # Network rows
    net_rows = ""
    for iface in net.get("interfaces", []):
        is_up = iface.get("is_up", False)
        status_badge = '<span class="badge badge-success">UP</span>' if is_up else '<span class="badge badge-danger">DOWN</span>'
        iface_esc = html.escape(str(iface.get('interface', '')))
        ip_esc = html.escape(str(iface.get('ip_address', '')))
        mac_esc = html.escape(str(iface.get('mac_address', '')))
        net_rows += f"""
        <tr>
            <td><code>{iface_esc}</code></td>
            <td>{status_badge}</td>
            <td><code>{ip_esc}</code></td>
            <td><code>{mac_esc}</code></td>
        </tr>
        """

    # Audit section
    audit_section = ""
    if audit_results:
        audit_rows = ""
        for r in audit_results:
            passed = getattr(r, "passed", False)
            p_name = html.escape(str(getattr(r, "policy_name", "Policy")))
            msg = html.escape(str(getattr(r, "message", "")))
            sev = html.escape(str(getattr(r, "severity", "MEDIUM")))
            status_b = '<span class="badge badge-success">PASSED</span>' if passed else '<span class="badge badge-danger">VIOLATION</span>'
            audit_rows += f"""
            <tr>
                <td><strong>{p_name}</strong></td>
                <td><span class="pill">{sev}</span></td>
                <td>{status_b}</td>
                <td>{msg}</td>
            </tr>
            """
        audit_section = f"""
        <div class="card">
            <h2>🛡️ {t('security_audit')}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{t('policy')}</th>
                        <th>{t('severity')}</th>
                        <th>{t('status')}</th>
                        <th>{t('details')}</th>
                    </tr>
                </thead>
                <tbody>
                    {audit_rows}
                </tbody>
            </table>
        </div>
        """

    host_esc = html.escape(str(sys.get('hostname', 'localhost')))
    os_esc = html.escape(str(sys.get('operating_system', 'N/A')))
    kernel_esc = html.escape(str(sys.get('kernel', 'N/A')))
    arch_esc = html.escape(str(sys.get('architecture', 'N/A')))
    py_esc = html.escape(str(sys.get('python_version', 'N/A')))
    user_esc = html.escape(str(sys.get('current_user', 'N/A')))

    html_content = f"""<!DOCTYPE html>
<html lang="{lang_code}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ITAT System Report - {host_esc}</title>
    <style>
        :root {{
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: #334155;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --accent-color: #38bdf8;
            --success-color: #22c55e;
            --warning-color: #f59e0b;
            --danger-color: #ef4444;
        }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }}
        .header h1 {{
            margin: 0;
            font-size: 1.8rem;
            color: var(--accent-color);
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        .card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
            margin-bottom: 1.5rem;
        }}
        .card h2 {{
            margin-top: 0;
            font-size: 1.2rem;
            color: var(--accent-color);
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 0.5rem;
        }}
        .metric-row {{
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px dashed rgba(255,255,255,0.05);
        }}
        .metric-label {{
            color: var(--text-muted);
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        th, td {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid var(--border-color);
        }}
        th {{
            color: var(--accent-color);
            font-weight: 600;
        }}
        code {{
            background: rgba(15, 23, 42, 0.8);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: monospace;
            color: #e2e8f0;
        }}
        .badge {{
            padding: 0.25rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .badge-success {{ background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }}
        .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }}
        .badge-danger {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }}
        .pill {{
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-color);
            padding: 0.1rem 0.5rem;
            border-radius: 6px;
            font-size: 0.85rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>IT Automation Toolkit</h1>
                <span class="text-muted">{t('exec_report')}</span>
            </div>
            <div>
                <span class="pill">Host: {host_esc}</span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>🖥️ {t('system_overview')}</h2>
                <div class="metric-row"><span class="metric-label">OS:</span><span>{os_esc}</span></div>
                <div class="metric-row"><span class="metric-label">Kernel:</span><span>{kernel_esc}</span></div>
                <div class="metric-row"><span class="metric-label">Architecture:</span><span>{arch_esc}</span></div>
                <div class="metric-row"><span class="metric-label">Python:</span><span>{py_esc}</span></div>
                <div class="metric-row"><span class="metric-label">User:</span><span>{user_esc}</span></div>
            </div>

            <div class="card">
                <h2>⚡ {t('hardware_resources')}</h2>
                <div class="metric-row"><span class="metric-label">CPU Cores:</span><span>{cpu.get('physical_cores')} Physical / {cpu.get('logical_cores')} Logical</span></div>
                <div class="metric-row"><span class="metric-label">CPU Frequency:</span><span>{cpu.get('current_frequency')} MHz</span></div>
                <div class="metric-row"><span class="metric-label">RAM Usage:</span><span>{mem.get('used_gb')} GB / {mem.get('total_gb')} GB ({mem.get('used_percent')}%)</span></div>
                <div class="metric-row"><span class="metric-label">Swap Usage:</span><span>{mem.get('swap_used_gb')} GB / {mem.get('swap_total_gb')} GB</span></div>
            </div>
        </div>

        {audit_section}

        <div class="card">
            <h2>💽 {t('storage_partitions')}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{t('device')}</th>
                        <th>{t('mountpoint')}</th>
                        <th>{t('filesystem')}</th>
                        <th>{t('usage')}</th>
                        <th>{t('free')}</th>
                        <th>{t('percent')}</th>
                    </tr>
                </thead>
                <tbody>
                    {disk_rows}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>🌐 {t('network_interfaces')}</h2>
            <table>
                <thead>
                    <tr>
                        <th>{t('interface')}</th>
                        <th>{t('status')}</th>
                        <th>{t('ip_address')}</th>
                        <th>{t('mac_address')}</th>
                    </tr>
                </thead>
                <tbody>
                    {net_rows}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path
