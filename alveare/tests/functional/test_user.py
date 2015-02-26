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
