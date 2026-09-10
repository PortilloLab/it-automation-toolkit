"""
ITAT Reports package.
"""

from .html import generate_html_report
from .pdf import generate_pdf_report

__all__ = ["generate_html_report", "generate_pdf_report"]
