import unittest

from . import AlveareModelTestCase
from alveare.models import TicketSnapshot, Ticket, Project, Organization
from alveare.common.mock import create_one_snapshot

class TestTicketSnapshotModel(AlveareModelTestCase):

    def test_create(self):
        snap = create_one_snapshot(self.db)
        self.db.session.commit()

        ticket = snap.ticket
        project = ticket.project
        org = project.organization
    
        self.assertTrue(ticket)
        self.assertTrue(project)
        self.assertTrue(org)

    def test_delete_ticket(self):
        snap = create_one_snapshot(self.db)
        self.db.session.commit()

        ticket = snap.ticket
        ticket_id = ticket.id
        snap_id = snap.id

        self.db.session.delete(ticket)
        self.db.session.commit()

        self.assertFalse(Ticket.query.get(ticket_id))
        self.assertFalse(TicketSnapshot.query.get(snap_id))

    def test_delete_project(self):
        snap = create_one_snapshot(self.db)
        self.db.session.commit()

        ticket = snap.ticket
        project = ticket.project

        self.db.session.delete(project)
        self.db.session.commit()

