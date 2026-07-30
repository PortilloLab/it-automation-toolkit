"""
Data serialization and normalization utilities.
"""

from dataclasses import is_dataclass, asdict
from typing import Any


def to_dict(obj: Any) -> Any:
    """
    Recursively convert dataclass objects and structures into primitive dictionaries and lists.
    """
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: to_dict(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_dict(item) for item in obj]
    return obj
