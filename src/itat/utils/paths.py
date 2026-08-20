"""
Path management utilities for ITAT exports and configuration.
"""

import os


def ensure_export_path(filepath: str, default_filename: str = "report.html") -> str:
    """
    Ensures export destination directory exists.
    If filepath is just a filename (e.g. 'inventory.html'), it routes it to the './exports/' directory.

    :param filepath: Target file path or filename.
    :param default_filename: Fallback filename if empty.
    :return: Sanitized and prepared file path.
    """
    target = (filepath or default_filename).strip()

    dirname = os.path.dirname(target)
    if not dirname:
        # Simple filename provided; place into 'exports/' folder
        exports_dir = os.path.abspath("exports")
        os.makedirs(exports_dir, exist_ok=True)
        return os.path.join(exports_dir, target)
    else:
        os.makedirs(os.path.abspath(dirname), exist_ok=True)
        return target
