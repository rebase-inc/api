import json
import time
import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.common.utils import AlveareResource, validate_resource_collection
from alveare.models import (
    User,
)
from alveare.tests.common.user import (
    case_nominated_users,
    case_contractor_users,
    case_manager_users,
    case_contractors_with_contractor,
)

class TestUserResource(AlveareRestTestCase):
    def setUp(self):
        self.user_resource =        AlveareResource(self, 'User')
        super().setUp()

    def test_get_all_as_admin(self):
        self.login_admin()
        response = self.get_resource('users', expected_code = 200)
        self.assertIn('users', response)

    def test_create_new_as_admin(self):
        self.login_admin()
        user = dict(first_name='Saul', last_name='Goodman', email='saulgoodman@alveare.io', password='foo')

        expected_response = copy.copy(user)
        expected_response['admin'] = False
        expected_response['roles'] = []
        expected_response.pop('password')

        response = self.post_resource('users', user)
        last_seen = response['user'].pop('last_seen') # we don't know the exact time anyways
        user_id = response['user'].pop('id') # we don't know the id the database will give it

        self.assertNotIn('password', response['user'])
        self.assertEqual(response['user'], expected_response)

        response = self.get_resource('users/{}'.format(user_id))
        expected_response['last_seen'] = last_seen
        expected_response['id'] = user_id

        self.assertEqual(response['user'], expected_response)

    def _create_user(self, validate=None):
        return self.user_resource.create(
            validate=validate,
            expected_status=201,
            first_name='Saul',
            last_name='Goodman',
            email='saulgoodman@alveare.io',
            password='foo'
        )

    def test_create_anonymous(self):
        def validate_user(test_resource, user_data, response):
            del user_data['password']
            self.login(user_data['email'], 'foo')
            return test_resource.validate_response(user_data, response)

        user = self._create_user(validate=validate_user)

    def test_update_unauthorized(self):
        user = self._create_user()
        user['last_name'] = 'Badman'
        self.user_resource.update(expected_status=401, **user)

    def test_update(self):
        user = self._create_user()
        self.login(user['email'], 'foo')
        user['last_name'] = 'Badman'
        self.user_resource.update(**user)

    def test_update_as_admin(self):
        self.login_admin()
        user = dict(first_name='Walter', last_name='White', email='walterwhite@alveare.io', password='heisenberg')
        response = self.post_resource('users', user)
        user['id'] = response['user']['id']
        user['last_seen'] = response['user']['last_seen']
        user.pop('password') # it shouldn't be returned

        new_name = dict(first_name = 'Jesse', last_name = 'Pinkman')
        response = self.put_resource('users/{}'.format(user['id']), new_name)
        user.update(new_name)
        user['admin'] = False
        user['roles'] = []
        self.assertEqual(user, response['user'])

        new_email = dict(email = 'jessepinkman@alveare.io')
        response = self.put_resource('users/{}'.format(user['id']), new_email)
        user.update(new_email)
        self.assertEqual(user, response['user'])

    def test_delete_as_admin(self):
        self.login_admin()
        user = dict(first_name='Hank', last_name='Schrader', email='hankschrader@alveare.io', password='theyreminerals')
        response = self.post_resource('users', user)
        user_id = response['user']['id']
        response = self.delete_resource('users/{}'.format(user_id))
        response = self.get_resource('users/{}'.format(user_id), expected_code=404)

    def test_delete_unauthorized(self):
        user = self._create_user()
        user['last_name'] = 'Badman'
        self.user_resource.delete(expected_status=401, **user)

    def test_delete(self):
        user = self._create_user()
        self.login(user['email'], 'foo')
        user['last_name'] = 'Badman'
        self.user_resource.delete(validate=False, **user)


class TestUser(AlveareNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = AlveareResource(self, 'User')

    def test_get_all_manager_users(self):
        validate_resource_collection(self, *case_manager_users(self.db))

    def test_get_all_contractor_users(self):
        logged_in_user, expected_contractor_users = case_contractor_users(self.db)
        validate_resource_collection(self, logged_in_user, expected_contractor_users+[logged_in_user])

    def test_get_all_nominated_users(self):
        logged_in_user, expected_nominated_users = case_nominated_users(self.db)
        validate_resource_collection(self, logged_in_user, expected_nominated_users+[logged_in_user])

    def test_get_all_other_contractor_users(self):
        logged_in_user, manager_users, expected_contractor_users = case_contractors_with_contractor(self.db)
        expected_users = manager_users + expected_contractor_users
        validate_resource_collection(self, logged_in_user, expected_users)
