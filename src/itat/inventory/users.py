"""
System User inventory collector module.
"""

from dataclasses import dataclass, field
from typing import List
import psutil


@dataclass
class UserSessionInfo:
    """Represents an active system user session."""

    username: str
    terminal: str
    host: str
    started_at: float


@dataclass
class UserInventory:
    """Consolidated system users inventory."""

    active_users: List[UserSessionInfo] = field(default_factory=list)
    total_active_sessions: int = 0


def collect_user_inventory() -> UserInventory:
    """
    Collect active logged-in user sessions using psutil.
    """
    sessions = []
    try:
        raw_users = psutil.users()
        for u in raw_users:
            sessions.append(
                UserSessionInfo(
                    username=u.name,
                    terminal=u.terminal or "N/A",
                    host=u.host or "localhost",
                    started_at=u.started,
                )
            )
    except Exception:
        pass

    return UserInventory(
        active_users=sessions,
        total_active_sessions=len(sessions),
    )
