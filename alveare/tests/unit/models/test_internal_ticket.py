import unittest
import datetime

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestInternalTicketModel(AlveareModelTestCase):

    def test_create(self):
        ticket = mock.create_one_internal_ticket(self.db, 'Foobar')
        self.db.session.commit()
        found_ticket = models.Ticket.query.get(ticket.id)
        self.assertIsInstance(found_ticket, models.Ticket)
        self.assertIsInstance(found_ticket, models.InternalTicket)
        self.assertEqual(found_ticket.snapshots, [])
        self.assertIsInstance(found_ticket.project, models.Project)

    def test_delete(self):
        ticket = mock.create_one_internal_ticket(self.db, 'Foobar')
        comment = models.Comment(ticket, 'heyo')
        self.db.session.commit()
        ticket_id = ticket.id
        comment_id = comment.id

        found_ticket = models.Ticket.query.get(ticket_id)
        self.db.session.delete(found_ticket)
        self.db.session.commit()

        self.assertEqual(models.Ticket.query.get(ticket_id), None)
        self.assertEqual(models.Comment.query.get(comment_id), None)

    def test_update(self):
        ticket = mock.create_one_internal_ticket(self.db, 'Foobar')
        self.db.session.commit()

        new_title = ticket.title + 'foo'
        new_description = ticket.title + 'bar'

        ticket.title = new_title
        ticket.description = new_description

        self.db.session.commit()

        found_ticket = models.Ticket.query.get(ticket.id)
        self.assertIsInstance(found_ticket, models.InternalTicket)
        
        self.assertEqual(found_ticket.title, new_title)
        self.assertEqual(found_ticket.description, new_description)

