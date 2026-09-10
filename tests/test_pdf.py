"""
Tests for Corporate PDF Report Generator and CLI integration.
"""

import os
import shutil
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
import pytest

from itat.reports.pdf import PDFCanvas, CorporatePDFReportBuilder, generate_pdf_report
from itat.policies.base import PolicyResult
from itat.commands.inventory import InventoryCommand
from itat.commands.audit import AuditCommand


@pytest.fixture
def sample_inventory():
    return {
        "system": {
            "hostname": "srv-corporate-01",
            "operating_system": "Linux Ubuntu 24.04 LTS",
            "kernel": "6.8.0-31-generic",
            "architecture": "x86_64",
            "python_version": "3.13.7",
            "current_user": "jose",
        },
        "cpu": {
            "physical_cores": 8,
            "logical_cores": 16,
            "usage_percent": 14.5,
        },
        "memory": {
            "total_gb": 32.0,
            "used_gb": 12.5,
            "used_percent": 39.1,
            "swap_total_gb": 8.0,
            "swap_used_gb": 0.5,
            "swap_percent": 6.25,
        },
        "disk": {
            "partitions": [
                {
                    "device": "/dev/nvme0n1p2",
                    "mountpoint": "/",
                    "fstype": "ext4",
                    "total_gb": 500.0,
                    "used_gb": 180.0,
                    "used_percent": 36.0,
                },
                {
                    "device": "/dev/sda1",
                    "mountpoint": "/data",
                    "fstype": "xfs",
                    "total_gb": 2000.0,
                    "used_gb": 1650.0,
                    "used_percent": 82.5,
                },
            ]
        },
        "network": {
            "interfaces": [
                {
                    "interface": "eth0",
                    "is_up": True,
                    "ip_address": "192.168.1.50",
                    "mac_address": "00:1A:2B:3C:4D:5E",
                },
                {
                    "interface": "wlan0",
                    "is_up": False,
                    "ip_address": None,
                    "mac_address": "00:1A:2B:3C:4D:5F",
                },
            ]
        },
    }


@pytest.fixture
def sample_audit_results():
    return [
        PolicyResult(
            policy_name="Disk Space Compliance",
            passed=True,
            severity="HIGH",
            message="All disk partitions within limit.",
        ),
        PolicyResult(
            policy_name="RAM Usage Compliance",
            passed=False,
            severity="MEDIUM",
            message="RAM usage is high: 88.0% (Limit: 85.0%)",
        ),
        PolicyResult(
            policy_name="Root Execution Security",
            passed=False,
            severity="CRITICAL",
            message="Service running under root account!",
        ),
    ]


class TestPDFCanvas:

    def test_canvas_primitives_render(self):
        canvas = PDFCanvas(page_width=612.0, page_height=792.0)
        canvas.draw_rect(50, 700, 200, 50, fill_color=(0.1, 0.2, 0.3))
        canvas.draw_line(50, 680, 250, 680, stroke_color=(0.5, 0.5, 0.5), line_width=2.0)
        canvas.draw_text("Auditoría de Sistemas", 50, 650, font="Helvetica-Bold", size=14.0)
        canvas.draw_pill("PASSED", 50, 600, 60, 18, bg_color=(0.1, 0.7, 0.3))

        pdf_bytes = canvas.render()
        assert pdf_bytes.startswith(b"%PDF-1.4\n")
        assert b"trailer\n" in pdf_bytes
        assert b"%%EOF\n" in pdf_bytes
        assert b"Auditor" in pdf_bytes

    def test_canvas_text_sanitization(self):
        text = "Auditoría • Seguridad & Cumplimiento — Prueba ‘OK’"
        clean = PDFCanvas.sanitize(text)
        assert "•" not in clean
        assert "—" not in clean
        assert "í" in clean  # Latin-1 preserves standard accents in NFC


class TestPDFReportBuilder:

    def test_generate_pdf_report_file(self, sample_inventory, sample_audit_results):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pdf") as f:
            pdf_path = f.name

        try:
            res_path = generate_pdf_report(
                inventory_data=sample_inventory,
                audit_results=sample_audit_results,
                output_path=pdf_path,
                client_name="Alpha Corp",
                environment="Staging",
            )

            assert os.path.exists(res_path)
            file_size = os.path.getsize(res_path)
            assert file_size > 1500  # Substantial PDF document

            with open(res_path, "rb") as f:
                header = f.read(8)
                assert header == b"%PDF-1.4"
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)

    def test_pdftotext_extraction(self, sample_inventory, sample_audit_results):
        """If pdftotext is available on the system, verify text extraction fidelity."""
        if not shutil.which("pdftotext"):
            pytest.skip("pdftotext command line utility not installed")

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pdf") as f:
            pdf_path = f.name

        try:
            generate_pdf_report(
                inventory_data=sample_inventory,
                audit_results=sample_audit_results,
                output_path=pdf_path,
                client_name="Beta International",
                environment="Production",
            )

            proc = subprocess.run(
                ["pdftotext", pdf_path, "-"],
                capture_output=True,
                text=True,
                check=True,
            )
            extracted_text = proc.stdout

            assert "IT AUTOMATION TOOLKIT" in extracted_text
            assert "Beta International" in extracted_text
            assert "srv-corporate-01" in extracted_text
            assert "Disk Space Compliance" in extracted_text
            assert "PASSED" in extracted_text
            assert "CRITICAL" in extracted_text
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


class TestCLICommandsPDFIntegration:

    def test_inventory_command_pdf(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pdf") as f:
            temp_pdf = f.name

        try:
            cmd = InventoryCommand()
            ret = cmd.run(["--pdf", temp_pdf])
            assert ret == 0
            assert os.path.exists(temp_pdf)
            assert os.path.getsize(temp_pdf) > 1000
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)

    def test_audit_command_pdf(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".pdf") as f:
            temp_pdf = f.name

        try:
            cmd = AuditCommand()
            # Run with --no-alerts so we don't trigger external webhooks
            ret = cmd.run(["--pdf", temp_pdf, "--no-alerts"])
            assert os.path.exists(temp_pdf)
            assert os.path.getsize(temp_pdf) > 1000
        finally:
            if os.path.exists(temp_pdf):
                os.remove(temp_pdf)
