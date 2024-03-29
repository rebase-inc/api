import unittest

from . import RebaseModelTestCase
from rebase.models import Contractor, RemoteWorkHistory
from rebase.common.mock import create_one_remote_work_history

class TestRemoteWorkHistoryModel(RebaseModelTestCase):

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

        self.assertEqual( RemoteWorkHistory.query.all(), [])

    def test_delete_orphan(self):
        remote_work_history = create_one_remote_work_history(self.db)
        self.db.session.commit()

        contractor = remote_work_history.contractor
        # unrelates contractor from its only remote_work_history instance
        # that should trigger a deletion of the rwh because of the 'delete-orphan' clause
        # in the relationship definition
        remote_work_history_id = remote_work_history.id
        contractor.remote_work_history = None

        self.assertNotEqual( Contractor.query.all(), [])
        self.assertFalse( RemoteWorkHistory.query.get(remote_work_history_id) )


    def test_bad_create(self):
        with self.assertRaises(ValueError):
            history = create_one_remote_work_history(self.db, contractor='bullshit')
            self.db.session.commit()
