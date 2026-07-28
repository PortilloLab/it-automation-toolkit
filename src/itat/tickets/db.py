"""
SQLite Ticket Database for ITAT Support & ITSM module.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class TicketDatabase:
    """
    Manages local SQLite database for IT support tickets.
    """

    def __init__(self, db_path: Optional[str] = None):
        if not db_path:
            config_dir = os.path.expanduser("~/.itat")
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, "tickets.db")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tickets table if not exists."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    client_name TEXT DEFAULT 'General Client',
                    priority TEXT DEFAULT 'MEDIUM',
                    status TEXT DEFAULT 'OPEN',
                    skill_name TEXT,
                    created_at TEXT NOT NULL,
                    resolved_at TEXT,
                    resolution_notes TEXT
                )
            """)
            conn.commit()

    def create_ticket(
        self,
        title: str,
        description: str = "",
        client_name: str = "General Client",
        priority: str = "MEDIUM",
        skill_name: str = "",
    ) -> int:
        """Create a new support ticket."""
        now = datetime.now().isoformat(timespec="seconds")
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tickets (title, description, client_name, priority, status, skill_name, created_at)
                VALUES (?, ?, ?, ?, 'OPEN', ?, ?)
                """,
                (title, description, client_name, priority.upper(), skill_name, now),
            )
            conn.commit()
            return cursor.lastrowid

    def list_tickets(
        self, status: Optional[str] = None, client_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List tickets with optional status or client filters."""
        query = "SELECT * FROM tickets WHERE 1=1"
        params = []

        if status:
            query += " AND status = ?"
            params.append(status.upper())
        if client_name:
            query += " AND client_name LIKE ?"
            params.append(f"%{client_name}%")

        query += " ORDER BY id DESC"

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_ticket(self, ticket_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a ticket by ID."""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
            return dict(row) if row else None

    def resolve_ticket(self, ticket_id: int, notes: str = "") -> bool:
        """Mark a ticket as RESOLVED with resolution notes."""
        now = datetime.now().isoformat(timespec="seconds")
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE tickets
                SET status = 'RESOLVED', resolved_at = ?, resolution_notes = ?
                WHERE id = ?
                """,
                (now, notes, ticket_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_ticket(self, ticket_id: int) -> bool:
        """Delete a ticket by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tickets WHERE id = ?", (ticket_id,))
            conn.commit()
            return cursor.rowcount > 0
