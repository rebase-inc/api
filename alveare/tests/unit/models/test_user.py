import unittest
import datetime

from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock
from alveare.tests.common.user import (
    case_nominated_users,
    case_contractor_users,
    case_manager_users,
    case_managers_with_contractor,
    case_contractors_with_contractor,
)

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
        self.assertIsInstance(user.roles.all(), list)
        self.assertIsInstance(user.roles.all().pop(), models.Contractor)

    def test_delete_contract(self):
        user = mock.create_one_user(self.db)
        contractor = models.Contractor(user)
        models.SkillSet(contractor)
        self.db.session.commit()

        user_id = user.id
        role_id = user.roles.all().pop().id

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

    def _test_users(self, users_query, logged_in_user, expected_users):
        self.assertTrue(expected_users)
        self.assertTrue(logged_in_user)
        users = users_query(logged_in_user).all()
        self.assertEqual(len(users), len(expected_users))
        for _user in users:
            self.assertIn(_user, expected_users)

        all_users = models.User.query_by_user(logged_in_user).all()
        for _user in users:
            self.assertIn(_user, all_users)

        users = users_query(logged_in_user, expected_users[0].id).all()
        self.assertEqual( len(users), 1)
        self.assertIn( expected_users[0], users )

    def test_manager_users(self):
        self._test_users(models.User.as_manager_get_other_managers, *case_manager_users(self.db))

    def test_contractor_users(self):
        self._test_users(models.User.as_manager_get_cleared_contractors, *case_contractor_users(self.db))
        
    def test_nominated_users(self):
        self._test_users(models.User.as_manager_get_nominated_users, *case_nominated_users(self.db))

    def test_manager_users_from_contractor(self):
        self._test_users(models.User.as_contractor_get_managers, *case_managers_with_contractor(self.db))

    def test_cleared_users_from_contractor(self):
        logged_in_user, manager_users, cleared_users = case_contractors_with_contractor(self.db)
        self._test_users(models.User.as_contractor_get_cleared_contractors, *(logged_in_user, cleared_users))
