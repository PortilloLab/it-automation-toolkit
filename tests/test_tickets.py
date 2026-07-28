"""
Unit tests for ITAT Ticket System and i18n module.
"""

import os
import tempfile
from itat.tickets.db import TicketDatabase
from itat.i18n.translator import Translator


def test_i18n_translator():
    trans = Translator("es")
    assert trans("inventory") == "Inventario del Sistema"
    trans.set_language("en")
    assert trans("inventory") == "System Inventory"


def test_ticket_database():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        db = TicketDatabase(db_path)
        ticket_id = db.create_ticket(
            title="Test Incident",
            description="Test DB issue",
            client_name="Test Client",
            priority="HIGH",
        )
        assert ticket_id == 1

        tickets = db.list_tickets()
        assert len(tickets) == 1
        assert tickets[0]["title"] == "Test Incident"

        success = db.resolve_ticket(ticket_id, notes="Resolved in test")
        assert success is True

        resolved_ticket = db.get_ticket(ticket_id)
        assert resolved_ticket["status"] == "RESOLVED"
        assert resolved_ticket["resolution_notes"] == "Resolved in test"

    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


if __name__ == "__main__":
    test_i18n_translator()
    test_ticket_database()
    print("All ticket and i18n unit tests passed!")
