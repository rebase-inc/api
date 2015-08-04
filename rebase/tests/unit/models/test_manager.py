import unittest
import datetime

from . import RebaseModelTestCase

from rebase.common import mock

from rebase.models.manager import Manager
from rebase.models.user import User
from rebase.models.organization import Organization

class TestManagerModel(RebaseModelTestCase):

    def test_create(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        self.assertNotEqual(Manager.query.get(manager.id), None)
        manager = Manager.query.get(manager.id)
        self.assertIsInstance(manager.user, User)
        self.assertIsInstance(manager.organization, Organization)

    def test_delete(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        found_manager = Manager.query.get(manager.id)
        self.delete_instance(found_manager)

        self.assertEqual(Manager.query.get(manager.id), None)
        self.assertIsInstance(User.query.get(manager.id), User)
        self.assertIsInstance(Organization.query.get(manager.organization_id), Organization)

    def test_delete_organization(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()
        org = manager.organization
        org_id = org.id
        manager_id = manager.id
        user_id = manager.user.id
        self.db.session.delete(org)
        self.db.session.commit()
        self.assertFalse(Organization.query.get(org_id))
        self.assertFalse(Manager.query.get(manager_id))
        self.assertTrue(User.query.get(user_id))

    def test_delete_user(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        user_id = manager.user.id
        manager_id = manager.id
        self.db.session.delete(manager.user)
        self.db.session.commit()

        self.assertFalse(Manager.query.get(manager_id))
        self.assertFalse(User.query.get(user_id))

    @unittest.skip('Manager model doesnt have any updatable fields yet')
    def test_update(self):
        contract = self.create_model(self.model)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(Manager, 'foo', 'bar')
        with self.assertRaises(ValueError):
            self.create_model(Manager, 2, 'foo')

