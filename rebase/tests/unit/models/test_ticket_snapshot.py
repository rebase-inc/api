import unittest

from . import RebaseModelTestCase
from rebase.models import TicketSnapshot, Ticket, Project, Organization
from rebase.common.mock import create_one_snapshot
from rebase.common.utils import validate_query_fn
from rebase.tests.common.ticket_snapshot import (
    case_as_manager,
    case_past_work_as_contractor,
    case_auctions_as_contractor,
)

class TestTicketSnapshotModel(RebaseModelTestCase):

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

    def test_mgr(self):
        validate_query_fn(
            self,
            TicketSnapshot,
            case_as_manager,
            TicketSnapshot.as_manager,
            True, True, True, True
        )

    def test_past_work_contractor(self):
        validate_query_fn(
            self,
            TicketSnapshot,
            case_past_work_as_contractor,
            TicketSnapshot.as_contractor_work_offers,
            False, False, False, True
        )

    def test_auctions_as_contractor(self):
        validate_query_fn(
            self,
            TicketSnapshot,
            case_auctions_as_contractor,
            TicketSnapshot.as_contractor_auctions,
            False, False, False, True
        )
