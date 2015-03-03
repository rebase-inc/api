import json
import time
import copy

from . import AlveareRestTestCase

class TestUserResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('users', expected_code = 200)
        self.assertIn('users', response)

    def test_create_new(self):
        user = dict(first_name='Saul', last_name='Goodman', email='saulgoodman@alveare.io', password='foo')

        expected_response = copy.copy(user)
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

    def test_update(self):
        user = dict(first_name='Walter', last_name='White', email='walterwhite@alveare.io', password='heisenberg')
        response = self.post_resource('users', user)
        user['id'] = response['user']['id']
        user['last_seen'] = response['user']['last_seen']
        user.pop('password') # it shouldn't be returned

        new_name = dict(first_name = 'Jesse', last_name = 'Pinkman')
        response = self.put_resource('users/{}'.format(user['id']), new_name)
        user.update(new_name)
        self.assertEqual(user, response['user'])

        new_email = dict(email = 'jessepinkman@alveare.io')
        response = self.put_resource('users/{}'.format(user['id']), new_email)
        user.update(new_email)
        self.assertEqual(user, response['user'])

    def test_delete(self):
        user = dict(first_name='Hank', last_name='Schrader', email='hankschrader@alveare.io', password='theyreminerals')
        response = self.post_resource('users', user)
        user_id = response['user']['id']

        response = self.delete_resource('users/{}'.format(user_id))
        response = self.get_resource('users/{}'.format(user_id), expected_code=404)
