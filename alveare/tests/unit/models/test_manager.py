import unittest
import datetime

from . import AlveareModelTestCase

from alveare.common import mock

from alveare.models.manager import Manager
from alveare.models.user import User
from alveare.models.organization import Organization

class TestManagerModel(AlveareModelTestCase):

    def test_create(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        self.assertNotEqual(Manager.query.get(manager.id), None)
        manager = Manager.query.get(manager.id)
        self.assertIsInstance(manager.user, User)
        self.assertIsInstance(manager.organization, Organization)

    def test_delete_contract(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        manager_id = manager.id
        user_id = manager.user.id
        organization_id = manager.organization.id

        found_manager = Manager.query.get(manager_id)
        self.delete_instance(found_manager)

        self.assertEqual(Manager.query.get(manager_id), None)
        self.assertIsInstance(User.query.get(user_id), User)
        self.assertIsInstance(Organization.query.get(organization_id), Organization)

    @unittest.skip('Manager model doesnt have any updatable fields yet')
    def test_update(self):
        contract = self.create_model(self.model)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(Manager, 'foo', 'bar')
        with self.assertRaises(ValueError):
            self.create_model(Manager, 2, 'foo')

