import unittest
import datetime

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestManagerModel(AlveareModelTestCase):

    def test_create(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        manager = models.Manager.query.get(manager.id)
        self.assertIsInstance(manager.user, models.User)
        self.assertIsInstance(manager.organization, models.Organization)

    def test_delete_contract(self):
        manager = mock.create_one_manager(self.db)
        self.db.session.commit()

        manager_id = manager.id
        user_id = manager.user.id
        organization_id = manager.organization.id

        found_manager = models.Manager.query.get(manager_id)
        self.delete_instance(found_manager)

        self.assertEqual(models.Manager.query.get(manager_id), None)
        self.assertIsInstance(models.User.query.get(user_id), models.User)
        self.assertIsInstance(models.Organization.query.get(organization_id), models.Organization)

    @unittest.skip('Manager model doesnt have any updatable fields yet')
    def test_update(self):
        contract = self.create_model(self.model)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Manager, 'foo', 'bar')
        with self.assertRaises(ValueError):
            self.create_model(models.Manager, 2, 'foo')

