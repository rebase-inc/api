import unittest
import datetime

from sqlalchemy.orm.exc import ObjectDeletedError

from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock

#TODO: Make this actually work...github tickets shouldn't be modifiable but they currently are
class TestGithubTicketModel(RebaseModelTestCase):

    def test_create(self):
        ticket = mock.create_one_github_ticket(self.db, 1)
        self.db.session.commit()
        found_ticket = models.Ticket.query.get(ticket.id)
        self.assertIsInstance(found_ticket, models.Ticket)
        self.assertIsInstance(found_ticket, models.GithubTicket)
        self.assertEqual(found_ticket.snapshots, [])
        self.assertIsInstance(found_ticket.project, models.Project)

    def test_delete(self):
        ticket = mock.create_one_github_ticket(self.db, 1)
        comment = models.Comment('heyo', ticket=ticket)
        self.db.session.commit()
        ticket_id = ticket.id
        comment_id = comment.id

        found_ticket = models.Ticket.query.get(ticket_id)
        self.db.session.delete(found_ticket)
        self.db.session.commit()

        self.assertEqual(models.Ticket.query.get(ticket_id), None)
        self.assertEqual(models.Comment.query.get(comment_id), None)

    @unittest.skip('github ticket is not updatable')
    def test_update(self):
        pass 


