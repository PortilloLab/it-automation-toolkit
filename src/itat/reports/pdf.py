"""
Executive Corporate PDF Report Generator for ITAT.

Generates high-fidelity, corporate-grade PDF audit and inventory reports
with zero external C-dependencies (pure Python 3.11+ implementation).
Includes multi-page pagination, executive summary KPIs, policy compliance
breakdown, and detailed hardware/network inventory tables.
"""

import os
import datetime
import unicodedata
from typing import Any, Dict, List, Optional, Tuple
from itat.core.serialization import to_dict
from itat.utils.paths import ensure_export_path
from itat.i18n import t


class PDFCanvas:
    """
    Pure-Python PDF 1.4 Canvas for drawing vector graphics, colors, and WinAnsi typography.
    """

    FONTS = {
        "Helvetica": "/F1",
        "Helvetica-Bold": "/F2",
        "Courier": "/F3",
        "Courier-Bold": "/F4",
    }

    def __init__(self, page_width: float = 612.0, page_height: float = 792.0):
        self.width = page_width
        self.height = page_height
        self.pages_streams: List[bytearray] = []
        self.current_stream: bytearray = bytearray()
        self.new_page()

    def new_page(self) -> None:
        """Start a new page in the document."""
        if len(self.pages_streams) > 0 or len(self.current_stream) > 0:
            self.pages_streams.append(self.current_stream)
        self.current_stream = bytearray()

    def _append(self, cmd: str) -> None:
        self.current_stream.extend(cmd.encode("latin-1", "replace"))
        self.current_stream.append(10)  # \n

    @staticmethod
    def sanitize(text: str) -> str:
        """Sanitize unicode string for WinAnsi PDF typography."""
        if not text:
            return ""
        replacements = {
            "•": "-", "✓": "[OK]", "✗": "[X]", "—": "-", "–": "-",
            "“": '"', "”": '"', "‘": "'", "’": "'", "…": "...", "→": "->",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        text = unicodedata.normalize("NFC", str(text))
        return text.encode("latin-1", "replace").decode("latin-1")

    @classmethod
    def escape_pdf_string(cls, text: str) -> str:
        """Escape backslashes and parentheses for PDF string literal."""
        clean = cls.sanitize(text)
        clean = clean.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        return clean

    def set_fill_color(self, r: float, g: float, b: float) -> None:
        self._append(f"{r:.3f} {g:.3f} {b:.3f} rg")

    def set_stroke_color(self, r: float, g: float, b: float) -> None:
        self._append(f"{r:.3f} {g:.3f} {b:.3f} RG")

    def set_line_width(self, width: float) -> None:
        self._append(f"{width:.2f} w")

    def draw_rect(
        self,
        x: float,
        y: float,
        w: float,
        h: float,
        fill_color: Optional[Tuple[float, float, float]] = None,
        stroke_color: Optional[Tuple[float, float, float]] = None,
        line_width: float = 1.0,
    ) -> None:
        """Draw a filled and/or stroked rectangle."""
        self._append("q")
        if fill_color and stroke_color:
            self.set_fill_color(*fill_color)
            self.set_stroke_color(*stroke_color)
            self.set_line_width(line_width)
            self._append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re B")
        elif fill_color:
            self.set_fill_color(*fill_color)
            self._append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re f")
        elif stroke_color:
            self.set_stroke_color(*stroke_color)
            self.set_line_width(line_width)
            self._append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re s")
        self._append("Q")

    def draw_line(
        self,
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        stroke_color: Tuple[float, float, float] = (0.8, 0.8, 0.8),
        line_width: float = 1.0,
    ) -> None:
        self._append("q")
        self.set_stroke_color(*stroke_color)
        self.set_line_width(line_width)
        self._append(f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")
        self._append("Q")

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        font: str = "Helvetica",
        size: float = 10.0,
        color: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> None:
        font_ref = self.FONTS.get(font, "/F1")
        escaped = self.escape_pdf_string(text)
        self._append("BT")
        self.set_fill_color(*color)
        self._append(f"{font_ref} {size:.2f} Tf")
        self._append(f"{x:.2f} {y:.2f} Td")
        self._append(f"({escaped}) Tj")
        self._append("ET")

    def draw_pill(
        self,
        text: str,
        x: float,
        y: float,
        w: float,
        h: float,
        bg_color: Tuple[float, float, float],
        text_color: Tuple[float, float, float] = (1.0, 1.0, 1.0),
        font_size: float = 8.0,
    ) -> None:
        """Draw an executive badge pill."""
        self.draw_rect(x, y, w, h, fill_color=bg_color)
        # Approximate text centering
        text_len = len(text) * (font_size * 0.52)
        offset_x = max(2.0, (w - text_len) / 2.0)
        offset_y = (h - font_size) / 2.0 + 1.5
        self.draw_text(text, x + offset_x, y + offset_y, font="Helvetica-Bold", size=font_size, color=text_color)

    def render(self) -> bytes:
        """Render complete PDF document binary buffer."""
        # Ensure final stream is captured
        if len(self.current_stream) > 0:
            self.pages_streams.append(self.current_stream)
            self.current_stream = bytearray()

        total_pages = max(1, len(self.pages_streams))
        body = bytearray()
        body.extend(b"%PDF-1.4\n")

        offsets = {}
        next_obj_id = 1

        # Catalog obj
        cat_id = next_obj_id
        next_obj_id += 1

        # Pages obj
        pages_id = next_obj_id
        next_obj_id += 1

        # Fonts obj
        font_ids = {}
        fonts_config = [
            ("/F1", "Helvetica"),
            ("/F2", "Helvetica-Bold"),
            ("/F3", "Courier"),
            ("/F4", "Courier-Bold"),
        ]
        for ref, name in fonts_config:
            font_ids[ref] = next_obj_id
            next_obj_id += 1

        # Page & Content Stream Object IDs
        page_ids = []
        stream_ids = []
        for _ in range(total_pages):
            page_ids.append(next_obj_id)
            next_obj_id += 1
            stream_ids.append(next_obj_id)
            next_obj_id += 1

        # 1. Catalog
        offsets[cat_id] = len(body)
        body.extend(f"{cat_id} 0 obj\n<< /Type /Catalog /Pages {pages_id} 0 R >>\nendobj\n".encode("latin-1"))

        # 2. Pages
        offsets[pages_id] = len(body)
        kids = " ".join(f"{pid} 0 R" for pid in page_ids)
        body.extend(f"{pages_id} 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {total_pages} >>\nendobj\n".encode("latin-1"))

        # 3. Fonts
        for ref, name in fonts_config:
            fid = font_ids[ref]
            offsets[fid] = len(body)
            body.extend(
                f"{fid} 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /{name} /Encoding /WinAnsiEncoding >>\nendobj\n".encode("latin-1")
            )

        # 4. Pages and Streams
        fonts_dict = " ".join(f"{ref} {font_ids[ref]} 0 R" for ref, _ in fonts_config)
        for i in range(total_pages):
            pid = page_ids[i]
            sid = stream_ids[i]
            stream_data = self.pages_streams[i] if i < len(self.pages_streams) else b""

            # Page Object
            offsets[pid] = len(body)
            body.extend(
                f"{pid} 0 obj\n<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {self.width:.2f} {self.height:.2f}] "
                f"/Contents {sid} 0 R /Resources << /Font << {fonts_dict} >> >> >>\nendobj\n".encode("latin-1")
            )

            # Stream Object
            offsets[sid] = len(body)
            body.extend(
                f"{sid} 0 obj\n<< /Length {len(stream_data)} >>\nstream\n".encode("latin-1")
                + stream_data
                + b"\nendstream\nendobj\n"
            )

        # 5. XRef Table
        xref_offset = len(body)
        total_objects = next_obj_id
        body.extend(f"xref\n0 {total_objects}\n0000000000 65535 f \n".encode("latin-1"))
        for oid in range(1, total_objects):
            offset = offsets.get(oid, 0)
            body.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

        # 6. Trailer
        body.extend(
            f"trailer\n<< /Size {total_objects} /Root {cat_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode("latin-1")
        )

        return bytes(body)


class CorporatePDFReportBuilder:
    """
    Constructs multi-page executive audit and inventory reports for ITAT.
    """

    # Theme colors
    C_PRIMARY = (0.06, 0.09, 0.16)       # #0F172A Dark Slate / Navy
    C_HEADER_BG = (0.12, 0.16, 0.24)     # #1E293B Deep Charcoal Slate
    C_ACCENT_BLUE = (0.15, 0.39, 0.92)   # #2563EB Royal Blue
    C_BG_CARD = (0.97, 0.98, 0.99)       # #F8FAFC Ultra light gray
    C_BORDER = (0.88, 0.91, 0.94)        # #E2E8F0 Border gray
    C_TEXT_MAIN = (0.06, 0.09, 0.16)     # #0F172A Primary text
    C_TEXT_MUTED = (0.39, 0.45, 0.55)    # #64748B Secondary text
    C_WHITE = (1.0, 1.0, 1.0)

    C_SUCCESS = (0.09, 0.64, 0.29)       # #16A34A Emerald Green
    C_WARNING = (0.85, 0.47, 0.02)       # #D97706 Amber Orange
    C_DANGER = (0.86, 0.15, 0.15)        # #DC2626 Crimson Red

    def __init__(
        self,
        inventory_data: Dict[str, Any],
        audit_results: Optional[List[Any]] = None,
        client_name: str = "Default Client",
        environment: str = "Production",
    ):
        self.inventory = to_dict(inventory_data)
        self.audit_results = audit_results or []
        self.client_name = client_name
        self.environment = environment

        self.canvas = PDFCanvas(page_width=612.0, page_height=792.0)
        self.margin_left = 40.0
        self.margin_right = 572.0
        self.content_width = self.margin_right - self.margin_left  # 532 pt
        self.page_number = 1
        self.cursor_y = 740.0

    def _check_page_break(self, needed_height: float) -> None:
        """If cursor would exceed bottom margin, advance to new page."""
        if self.cursor_y - needed_height < 60.0:
            self._draw_footer()
            self.canvas.new_page()
            self.page_number += 1
            self.cursor_y = 735.0
            self._draw_running_header()

    def _draw_running_header(self) -> None:
        """Top running header for page 2 and onwards."""
        self.canvas.draw_text(
            f"ITAT - {self.client_name} ({self.environment})",
            self.margin_left,
            750.0,
            font="Helvetica-Bold",
            size=9.0,
            color=self.C_TEXT_MUTED,
        )
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.canvas.draw_text(
            date_str,
            self.margin_right - 80.0,
            750.0,
            font="Helvetica",
            size=9.0,
            color=self.C_TEXT_MUTED,
        )
        self.canvas.draw_line(self.margin_left, 742.0, self.margin_right, 742.0, stroke_color=self.C_BORDER, line_width=0.75)
        self.cursor_y = 720.0

    def _draw_footer(self) -> None:
        """Bottom footer on every page."""
        self.canvas.draw_line(self.margin_left, 45.0, self.margin_right, 45.0, stroke_color=self.C_BORDER, line_width=0.75)
        self.canvas.draw_text(
            "Confidencial - Generado por PortilloLab IT Automation Toolkit (ITAT)",
            self.margin_left,
            32.0,
            font="Helvetica",
            size=8.0,
            color=self.C_TEXT_MUTED,
        )
        self.canvas.draw_text(
            f"Página {self.page_number}",
            self.margin_right - 45.0,
            32.0,
            font="Helvetica",
            size=8.0,
            color=self.C_TEXT_MUTED,
        )

    def draw_cover_banner(self) -> None:
        """Draw top executive header banner on first page."""
        banner_h = 86.0
        y = self.cursor_y - banner_h
        self.canvas.draw_rect(self.margin_left, y, self.content_width, banner_h, fill_color=self.C_HEADER_BG)

        # Left blue accent line
        self.canvas.draw_rect(self.margin_left, y, 5.0, banner_h, fill_color=self.C_ACCENT_BLUE)

        # Title & Subtitle
        self.canvas.draw_text(
            "IT AUTOMATION TOOLKIT (ITAT)",
            self.margin_left + 20.0,
            y + 54.0,
            font="Helvetica-Bold",
            size=16.0,
            color=self.C_WHITE,
        )
        self.canvas.draw_text(
            "INFORME EJECUTIVO DE AUDITORIA E INFRAESTRUCTURA",
            self.margin_left + 20.0,
            y + 38.0,
            font="Helvetica",
            size=9.5,
            color=(0.75, 0.85, 0.98),
        )

        # Meta tags on bottom of banner
        hostname = self.inventory.get("system", {}).get("hostname", "localhost")
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta_left = f"Cliente: {self.client_name}  |  Entorno: {self.environment}"
        meta_right = f"Host: {hostname}  |  Fecha: {now_str}"

        self.canvas.draw_text(
            meta_left,
            self.margin_left + 20.0,
            y + 15.0,
            font="Helvetica-Bold",
            size=8.5,
            color=(0.85, 0.90, 0.95),
        )
        self.canvas.draw_text(
            meta_right,
            self.margin_left + 270.0,
            y + 15.0,
            font="Helvetica",
            size=8.5,
            color=(0.80, 0.85, 0.92),
        )

        self.cursor_y = y - 20.0

    def draw_audit_kpis(self) -> None:
        """Draw 4 executive audit summary KPI cards."""
        if not self.audit_results:
            return

        self._check_page_break(75.0)

        total = len(self.audit_results)
        failures = sum(1 for r in self.audit_results if not getattr(r, "passed", True) and getattr(r, "severity", "") in ["HIGH", "CRITICAL"])
        warnings = sum(1 for r in self.audit_results if not getattr(r, "passed", True) and getattr(r, "severity", "") not in ["HIGH", "CRITICAL"])
        passed = total - failures - warnings

        cards = [
            ("TOTAL REGLAS", str(total), self.C_TEXT_MAIN, self.C_BORDER),
            ("CONFORMES", str(passed), self.C_SUCCESS, self.C_SUCCESS),
            ("ADVERTENCIAS", str(warnings), self.C_WARNING, self.C_WARNING),
            ("FALLOS CRITICOS", str(failures), self.C_DANGER, self.C_DANGER),
        ]

        card_w = (self.content_width - 30.0) / 4.0
        card_h = 56.0
        y = self.cursor_y - card_h

        for i, (label, value, val_color, border_color) in enumerate(cards):
            x = self.margin_left + i * (card_w + 10.0)
            self.canvas.draw_rect(x, y, card_w, card_h, fill_color=self.C_BG_CARD, stroke_color=self.C_BORDER, line_width=1.0)
            # Accent top bar
            self.canvas.draw_rect(x, y + card_h - 3.0, card_w, 3.0, fill_color=border_color)

            # Value
            self.canvas.draw_text(value, x + 12.0, y + 22.0, font="Helvetica-Bold", size=18.0, color=val_color)
            # Label
            self.canvas.draw_text(label, x + 12.0, y + 10.0, font="Helvetica-Bold", size=7.0, color=self.C_TEXT_MUTED)

        self.cursor_y = y - 20.0

    def draw_audit_table(self) -> None:
        """Draw policy audit breakdown table."""
        if not self.audit_results:
            return

        self._check_page_break(60.0)

        # Section Title
        self.canvas.draw_text("1. Auditoría de Seguridad y Cumplimiento de Políticas", self.margin_left, self.cursor_y, font="Helvetica-Bold", size=12.0, color=self.C_PRIMARY)
        self.cursor_y -= 14.0

        # Table Header
        th_h = 22.0
        self.canvas.draw_rect(self.margin_left, self.cursor_y - th_h, self.content_width, th_h, fill_color=self.C_HEADER_BG)
        self.canvas.draw_text("Politica Evaluada", self.margin_left + 10.0, self.cursor_y - 15.0, font="Helvetica-Bold", size=8.5, color=self.C_WHITE)
        self.canvas.draw_text("Severidad", self.margin_left + 180.0, self.cursor_y - 15.0, font="Helvetica-Bold", size=8.5, color=self.C_WHITE)
        self.canvas.draw_text("Estado", self.margin_left + 250.0, self.cursor_y - 15.0, font="Helvetica-Bold", size=8.5, color=self.C_WHITE)
        self.canvas.draw_text("Observaciones y Detalles", self.margin_left + 330.0, self.cursor_y - 15.0, font="Helvetica-Bold", size=8.5, color=self.C_WHITE)
        self.cursor_y -= th_h

        # Rows
        row_h = 26.0
        for i, res in enumerate(self.audit_results):
            self._check_page_break(row_h)

            bg_row = self.C_WHITE if i % 2 == 0 else self.C_BG_CARD
            y = self.cursor_y - row_h
            self.canvas.draw_rect(self.margin_left, y, self.content_width, row_h, fill_color=bg_row, stroke_color=self.C_BORDER, line_width=0.5)

            name = getattr(res, "policy_name", "Regla")[:25]
            severity = getattr(res, "severity", "INFO")
            is_passed = getattr(res, "passed", True)
            message = getattr(res, "message", "")[:45]

            # Policy Name
            self.canvas.draw_text(name, self.margin_left + 10.0, y + 9.0, font="Helvetica-Bold", size=8.0, color=self.C_TEXT_MAIN)

            # Severity Pill
            sev_bg = self.C_DANGER if severity == "CRITICAL" else (self.C_WARNING if severity in ["HIGH", "MEDIUM"] else self.C_TEXT_MUTED)
            self.canvas.draw_pill(severity, self.margin_left + 180.0, y + 6.0, 52.0, 14.0, bg_color=sev_bg, font_size=7.0)

            # Status Badge
            if is_passed:
                self.canvas.draw_pill("PASSED", self.margin_left + 248.0, y + 6.0, 62.0, 14.0, bg_color=self.C_SUCCESS, font_size=7.5)
            elif severity in ["HIGH", "CRITICAL"]:
                self.canvas.draw_pill("FAILED", self.margin_left + 248.0, y + 6.0, 62.0, 14.0, bg_color=self.C_DANGER, font_size=7.5)
            else:
                self.canvas.draw_pill("WARNING", self.margin_left + 248.0, y + 6.0, 62.0, 14.0, bg_color=self.C_WARNING, font_size=7.5)

            # Details
            self.canvas.draw_text(message, self.margin_left + 325.0, y + 9.0, font="Helvetica", size=7.5, color=self.C_TEXT_MUTED)

            self.cursor_y = y

        self.cursor_y -= 22.0

    def draw_inventory_section(self) -> None:
        """Draw system hardware, OS, and resource metrics."""
        self._check_page_break(130.0)

        title = "2. Diagnostico e Inventario de Infraestructura" if self.audit_results else "1. Inventario General del Sistema"
        self.canvas.draw_text(title, self.margin_left, self.cursor_y, font="Helvetica-Bold", size=12.0, color=self.C_PRIMARY)
        self.cursor_y -= 14.0

        sys = self.inventory.get("system", {})
        cpu = self.inventory.get("cpu", {})
        mem = self.inventory.get("memory", {})

        # Two cards side by side
        card_w = (self.content_width - 16.0) / 2.0
        card_h = 100.0
        y = self.cursor_y - card_h

        # Left Card: System & OS
        self.canvas.draw_rect(self.margin_left, y, card_w, card_h, fill_color=self.C_BG_CARD, stroke_color=self.C_BORDER)
        self.canvas.draw_rect(self.margin_left, y + card_h - 20.0, card_w, 20.0, fill_color=self.C_HEADER_BG)
        self.canvas.draw_text("SISTEMA OPERATIVO Y HOST", self.margin_left + 10.0, y + card_h - 14.0, font="Helvetica-Bold", size=8.0, color=self.C_WHITE)

        sys_fields = [
            ("Hostname:", str(sys.get("hostname", "N/A"))),
            ("S.O.:", f"{sys.get('operating_system', 'N/A')} ({sys.get('architecture', 'N/A')})"),
            ("Kernel:", str(sys.get("kernel", "N/A"))[:32]),
            ("Usuario actual:", str(sys.get("current_user", "N/A"))),
        ]
        for idx, (lbl, val) in enumerate(sys_fields):
            line_y = y + card_h - 36.0 - (idx * 15.0)
            self.canvas.draw_text(lbl, self.margin_left + 10.0, line_y, font="Helvetica-Bold", size=8.0, color=self.C_TEXT_MAIN)
            self.canvas.draw_text(val, self.margin_left + 90.0, line_y, font="Helvetica", size=8.0, color=self.C_TEXT_MUTED)

        # Right Card: Hardware Resources (CPU & RAM)
        rx = self.margin_left + card_w + 16.0
        self.canvas.draw_rect(rx, y, card_w, card_h, fill_color=self.C_BG_CARD, stroke_color=self.C_BORDER)
        self.canvas.draw_rect(rx, y + card_h - 20.0, card_w, 20.0, fill_color=self.C_HEADER_BG)
        self.canvas.draw_text("RECURSOS DE PROCESAMIENTO Y MEMORIA", rx + 10.0, y + card_h - 14.0, font="Helvetica-Bold", size=8.0, color=self.C_WHITE)

        cpu_cores = f"{cpu.get('physical_cores', 0)} físicos / {cpu.get('logical_cores', 0)} lógicos"
        cpu_usage = f"{cpu.get('usage_percent', 0)}%"
        ram_info = f"{mem.get('used_gb', 0)} GB / {mem.get('total_gb', 0)} GB ({mem.get('used_percent', 0)}%)"
        swap_info = f"{mem.get('swap_used_gb', 0)} GB / {mem.get('swap_total_gb', 0)} GB ({mem.get('swap_percent', 0)}%)"

        hw_fields = [
            ("CPU Núcleos:", cpu_cores),
            ("Uso CPU:", cpu_usage),
            ("Memoria RAM:", ram_info),
            ("Memoria Swap:", swap_info),
        ]
        for idx, (lbl, val) in enumerate(hw_fields):
            line_y = y + card_h - 36.0 - (idx * 15.0)
            self.canvas.draw_text(lbl, rx + 10.0, line_y, font="Helvetica-Bold", size=8.0, color=self.C_TEXT_MAIN)
            self.canvas.draw_text(val, rx + 95.0, line_y, font="Helvetica", size=8.0, color=self.C_TEXT_MUTED)

        self.cursor_y = y - 18.0

        # Storage Partitions Table
        self._draw_storage_table()

        # Network Interfaces Table
        self._draw_network_table()

    def _draw_storage_table(self) -> None:
        """Draw disk partitions table."""
        disk = self.inventory.get("disk", {})
        partitions = disk.get("partitions", [])
        if not partitions:
            return

        self._check_page_break(70.0)

        self.canvas.draw_text("Almacenamiento y Particiones de Disco", self.margin_left, self.cursor_y, font="Helvetica-Bold", size=9.5, color=self.C_PRIMARY)
        self.cursor_y -= 12.0

        th_h = 18.0
        self.canvas.draw_rect(self.margin_left, self.cursor_y - th_h, self.content_width, th_h, fill_color=(0.20, 0.25, 0.33))
        self.canvas.draw_text("Dispositivo", self.margin_left + 10.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Montaje", self.margin_left + 120.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Tipo", self.margin_left + 230.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Uso / Total", self.margin_left + 310.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Ocupación %", self.margin_left + 440.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.cursor_y -= th_h

        row_h = 20.0
        for i, part in enumerate(partitions[:8]):  # Limit to top 8 partitions to maintain clean layout
            self._check_page_break(row_h)
            y = self.cursor_y - row_h
            bg = self.C_WHITE if i % 2 == 0 else self.C_BG_CARD
            self.canvas.draw_rect(self.margin_left, y, self.content_width, row_h, fill_color=bg, stroke_color=self.C_BORDER, line_width=0.5)

            dev = str(part.get("device", ""))[:20]
            mount = str(part.get("mountpoint", ""))[:22]
            fstype = str(part.get("fstype", ""))[:12]
            usage = f"{part.get('used_gb', 0)} GB / {part.get('total_gb', 0)} GB"
            pct = float(part.get("used_percent", 0.0))

            self.canvas.draw_text(dev, self.margin_left + 10.0, y + 6.0, font="Courier", size=7.5, color=self.C_TEXT_MAIN)
            self.canvas.draw_text(mount, self.margin_left + 120.0, y + 6.0, font="Courier", size=7.5, color=self.C_TEXT_MAIN)
            self.canvas.draw_text(fstype, self.margin_left + 230.0, y + 6.0, font="Helvetica", size=7.5, color=self.C_TEXT_MUTED)
            self.canvas.draw_text(usage, self.margin_left + 310.0, y + 6.0, font="Helvetica", size=7.5, color=self.C_TEXT_MUTED)

            pct_color = self.C_DANGER if pct > 85.0 else (self.C_WARNING if pct > 70.0 else self.C_SUCCESS)
            self.canvas.draw_pill(f"{pct:.1f}%", self.margin_left + 440.0, y + 3.0, 48.0, 14.0, bg_color=pct_color, font_size=7.5)

            self.cursor_y = y

        self.cursor_y -= 16.0

    def _draw_network_table(self) -> None:
        """Draw network interfaces table."""
        net = self.inventory.get("network", {})
        interfaces = net.get("interfaces", [])
        if not interfaces:
            return

        self._check_page_break(70.0)

        self.canvas.draw_text("Interfaces de Red y Conectividad", self.margin_left, self.cursor_y, font="Helvetica-Bold", size=9.5, color=self.C_PRIMARY)
        self.cursor_y -= 12.0

        th_h = 18.0
        self.canvas.draw_rect(self.margin_left, self.cursor_y - th_h, self.content_width, th_h, fill_color=(0.20, 0.25, 0.33))
        self.canvas.draw_text("Interfaz", self.margin_left + 10.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Estado", self.margin_left + 130.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Dirección IPv4", self.margin_left + 220.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.canvas.draw_text("Dirección MAC", self.margin_left + 370.0, self.cursor_y - 12.0, font="Helvetica-Bold", size=7.5, color=self.C_WHITE)
        self.cursor_y -= th_h

        row_h = 20.0
        for i, iface in enumerate(interfaces[:8]):
            self._check_page_break(row_h)
            y = self.cursor_y - row_h
            bg = self.C_WHITE if i % 2 == 0 else self.C_BG_CARD
            self.canvas.draw_rect(self.margin_left, y, self.content_width, row_h, fill_color=bg, stroke_color=self.C_BORDER, line_width=0.5)

            name = str(iface.get("interface") or iface.get("name") or "eth0")[:18]
            is_up = bool(iface.get("is_up", False))
            ip = str(iface.get("ip_address") or iface.get("ip") or "Sin asignar")[:20]
            mac = str(iface.get("mac_address") or iface.get("mac") or "N/A")[:22]

            self.canvas.draw_text(name, self.margin_left + 10.0, y + 6.0, font="Courier", size=7.5, color=self.C_TEXT_MAIN)

            if is_up:
                self.canvas.draw_pill("UP", self.margin_left + 130.0, y + 3.0, 36.0, 14.0, bg_color=self.C_SUCCESS, font_size=7.0)
            else:
                self.canvas.draw_pill("DOWN", self.margin_left + 130.0, y + 3.0, 42.0, 14.0, bg_color=self.C_DANGER, font_size=7.0)

            self.canvas.draw_text(ip, self.margin_left + 220.0, y + 6.0, font="Courier", size=7.5, color=self.C_TEXT_MUTED)
            self.canvas.draw_text(mac, self.margin_left + 370.0, y + 6.0, font="Courier", size=7.5, color=self.C_TEXT_MUTED)

            self.cursor_y = y

        self.cursor_y -= 16.0

    def build(self) -> bytes:
        """Compile document and return PDF binary data."""
        self.draw_cover_banner()
        self.draw_audit_kpis()
        self.draw_audit_table()
        self.draw_inventory_section()
        self._draw_footer()
        return self.canvas.render()


def generate_pdf_report(
    inventory_data: Dict[str, Any],
    audit_results: Optional[List[Any]] = None,
    output_path: str = "report.pdf",
    client_name: str = "Default Client",
    environment: str = "Production",
) -> str:
    """
    Generate an executive PDF report and save it to output_path.

    :param inventory_data: System inventory dictionary.
    :param audit_results: Optional list of PolicyResult objects.
    :param output_path: Destination file path for PDF.
    :param client_name: Client name from profile.
    :param environment: Environment name (e.g. Production).
    :return: Sanitized and resolved output path.
    """
    output_path = ensure_export_path(output_path, "report.pdf")
    builder = CorporatePDFReportBuilder(
        inventory_data=inventory_data,
        audit_results=audit_results,
        client_name=client_name,
        environment=environment,
    )
    pdf_bytes = builder.build()

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return output_path
