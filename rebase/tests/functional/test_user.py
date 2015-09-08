import json
import time
import copy

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.common.utils import RebaseResource, validate_resource_collection
from rebase.models import (
    User,
)
from rebase.tests.common.user import (
    case_nominated_users,
    case_contractor_users,
    case_manager_users,
    case_contractors_with_contractor,
)

class TestUserResource(RebaseRestTestCase):
    def setUp(self):
        self.user_resource = RebaseResource(self, 'User')
        self.role_resource = RebaseResource(self, 'Role')
        super().setUp()

    def test_get_all_as_admin(self):
        self.login_admin()
        response = self.get_resource('users', expected_code = 200)
        self.assertIn('users', response)

    def _strip_role_ids(self, response):
        for role in response['user']['roles']:
            role.pop('id')

    def test_create_as_admin(self):
        self.login_admin()
        user = dict(first_name='Saul', last_name='Goodman', email='saulgoodman@rebase.io', password='foo')

        expected_response = copy.copy(user)
        expected_response['admin'] = False
        expected_response['roles'] = []
        expected_response.pop('password')

        response = self.post_resource('users', user)
        last_seen = response['user'].pop('last_seen') # we don't know the exact time anyways
        user_id = response['user'].pop('id') # we don't know the id the database will give it
        self._strip_role_ids(response)

        self.assertNotIn('password', response['user'])
        self.user_resource.assertComposite(expected_response, response['user'], recurse=True)

        response = self.get_resource('users/{}'.format(user_id))
        self._strip_role_ids(response)
        expected_response['last_seen'] = last_seen
        expected_response['id'] = user_id

        self.user_resource.assertComposite(expected_response, response['user'], recurse=True)

    def _create_user(self, validate=None):
        return self.user_resource.create(
            validate=validate,
            expected_status=201,
            first_name='Saul',
            last_name='Goodman',
            email='saulgoodman@rebase.io',
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
        user = self.user_resource.get(user)
        user['last_name'] = 'Badman'
        self.user_resource.update(**user)

    def test_update_as_admin(self):
        self.login_admin()
        user = dict(first_name='Walter', last_name='White', email='walterwhite@rebase.io', password='heisenberg')
        response = self.post_resource('users', user)
        user['id'] = response['user']['id']
        user['last_seen'] = response['user']['last_seen']
        user.pop('password') # it shouldn't be returned

        new_name = dict(first_name = 'Jesse', last_name = 'Pinkman')
        response = self.put_resource('users/{}'.format(user['id']), new_name)
        user.update(new_name)
        user['admin'] = False
        user['roles'] = []
        user['current_role'] = None
        self._strip_role_ids(response)
        self.assertEqual(user, response['user'])

        new_email = dict(email = 'jessepinkman@rebase.io')
        response = self.put_resource('users/{}'.format(user['id']), new_email)
        user.update(new_email)
        self._strip_role_ids(response)
        self.assertEqual(user, response['user'])

    def test_delete_as_admin(self):
        self.login_admin()
        user = dict(first_name='Hank', last_name='Schrader', email='hankschrader@rebase.io', password='theyreminerals')
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


class TestUser(RebaseNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = RebaseResource(self, 'User')

    def test_get_all_manager_users(self):
        mgr_user, users = self._run(case_manager_users, 'manager')
        validate_resource_collection(self, users)

    def test_get_all_contractor_users(self):
        logged_in_user, expected_contractor_users = self._run(case_contractor_users, 'contractor')
        validate_resource_collection(self, expected_contractor_users+[logged_in_user])

    def test_get_all_nominated_users(self):
        logged_in_user, expected_nominated_users = self._run(case_nominated_users, 'manager')
        validate_resource_collection(self, expected_nominated_users+[logged_in_user])

    def test_get_all_other_contractor_users(self):
        _, (manager_users, expected_contractor_users) = self._run(case_contractors_with_contractor, 'contractor')
        expected_users = manager_users + expected_contractor_users
        validate_resource_collection(self, expected_users)
