import unittest

from . import AlveareModelTestCase
from alveare.models import TicketSnapshot, Ticket, Project, Organization
from alveare.common.mock import create_one_snapshot
from alveare.tests.common.ticket_snapshot import (
    case_as_manager,
    case_past_work_as_contractor,
    case_auctions_as_contractor,
)

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

    def _test_query_fn(self, case, query_fn):
        user, snapshot = case(self.db)
        case(self.db) # create more unrelated snapshots, to make sure the queries discriminate properly
        snapshots = query_fn(user).all()
        self.assertEqual([snapshot], snapshots)
        self.assertEqual([snapshot], query_fn(user, snapshot.id).all())
        self.assertEqual([snapshot], TicketSnapshot.query_by_user(user).all())
        self.assertTrue(snapshot.allowed_to_be_viewed_by(user))

    def test_as_manager(self):
        self._test_query_fn(case_as_manager, TicketSnapshot.as_manager)
        user, snapshot = case_as_manager(self.db)
        self.assertTrue(snapshot.allowed_to_be_created_by(user))
        self.assertTrue(snapshot.allowed_to_be_deleted_by(user))
        self.assertTrue(snapshot.allowed_to_be_modified_by(user))

    def test_past_work_as_contractor(self):
        self._test_query_fn(case_past_work_as_contractor, TicketSnapshot.as_contractor_work_offers)
        user, snapshot = case_past_work_as_contractor(self.db)
        self.assertFalse(snapshot.allowed_to_be_created_by(user))
        self.assertFalse(snapshot.allowed_to_be_deleted_by(user))
        self.assertFalse(snapshot.allowed_to_be_modified_by(user))

    def test_auctions_as_contractor(self):
        self._test_query_fn(case_auctions_as_contractor, TicketSnapshot.as_contractor_auctions)
        user, snapshot = case_auctions_as_contractor(self.db)
        self.assertFalse(snapshot.allowed_to_be_created_by(user))
        self.assertFalse(snapshot.allowed_to_be_deleted_by(user))
        self.assertFalse(snapshot.allowed_to_be_modified_by(user))
