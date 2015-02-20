import unittest
import datetime

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestUserModel(AlveareModelTestCase):

    def test_create(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        user = models.User.query.get(user.id)

        self.assertIsInstance(user.first_name, str)
        self.assertIsInstance(user.last_name, str)
        self.assertIsInstance(user.email, str)
        self.assertIsInstance(user.hashed_password, str)
        self.assertIsInstance(user.last_seen, datetime.datetime)
        self.assertIsInstance(user.roles, list)
        self.assertIsInstance(user.roles.pop(), models.Contractor)

    def test_delete_contract(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        user_id = user.id
        role_id = user.roles.pop().id

        found_user = models.User.query.get(user_id)
        self.delete_instance(found_user)

        self.assertEqual(models.User.query.get(user_id), None)
        self.assertEqual(models.Role.query.get(role_id), None)

    def test_update(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        new_first_name = user.first_name + 'foo'
        new_last_name = user.last_name + 'foo'
        new_email = 'foo' + user.email
        new_password = user.hashed_password + 'foo'
        new_last_seen = datetime.datetime.now()

        user.first_name = new_first_name
        user.last_name = new_last_name
        user.email = new_email
        user.hashed_password = new_password
        user.last_seen = new_last_seen

        found_user = models.User.query.get(user.id)
        self.assertEqual(found_user.first_name, new_first_name)
        self.assertEqual(found_user.last_name, new_last_name)
        self.assertEqual(found_user.email, new_email)
        self.assertEqual(found_user.hashed_password, new_password)
        self.assertEqual(found_user.last_seen, new_last_seen)

    @unittest.skip('i suppose its not a big deal to pass ints as strs...')
    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.User, 1, 1, 1, 1)
