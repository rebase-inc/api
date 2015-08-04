import unittest
import datetime

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from rebase import models
from rebase.common import mock

class TestTicketModel(AlveareModelTestCase):

    def test_create(self):
        project = mock.create_one_project(self.db)
        with self.assertRaises(NotImplementedError):
            ticket = models.Ticket(project, 'foo')
            self.db.session.add(ticket)
            self.db.session.commit()

    @unittest.skip('Ticket model isnt implemented yet')
    def test_delete(self):
        pass

    def test_delete_auction(self):
        pass

    @unittest.skip('Ticket model doesnt have any updatable fields yet')
    def test_update(self):
        pass

    @unittest.skip('Ticket model doesnt have any creation fields yet')
    def test_bad_create(self):
        pass

