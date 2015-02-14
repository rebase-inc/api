import unittest

from . import AlveareModelTestCase
from alveare.models import Contractor, RemoteWorkHistory
from alveare.common.mock import create_one_remote_work_history

class TestRemoteWorkHistoryModel(AlveareModelTestCase):

    def test_create(self):
        remote_work_history = create_one_remote_work_history(self.db)
        self.db.session.commit()

        self.assertNotEqual( Contractor.query.all(), [])

    def test_delete(self):
        remote_work_history = create_one_remote_work_history(self.db)
        self.db.session.commit()
        self.delete_instance(remote_work_history)

        self.assertNotEqual( Contractor.query.all(), [])
        self.assertEqual( RemoteWorkHistory.query.all(), [])

    def test_delete_parent(self):
        remote_work_history = create_one_remote_work_history(self.db)
        self.db.session.commit()
        self.delete_instance(remote_work_history.contractor)

        self.assertEqual( Contractor.query.all(), [])
        self.assertEqual( RemoteWorkHistory.query.all(), [])


