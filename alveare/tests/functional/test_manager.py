import json
import time

from . import AlveareRestTestCase

class TestManagerResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('managers', expected_code = 200)
        self.assertIn('managers', response)

    def test_get_one(self):
        all_managers = self.get_resource('managers', expected_code = 200)
        self.assertEqual(len(all_managers['managers']), 1)
        manager = all_managers['managers'][0]
        response = self.get_resource('managers/{}'.format(manager['id']), expected_code = 200)
        self.assertIn('manager', response)
        same_manager = response['manager']

        self.assertEqual(manager['id'], same_manager['id'])

    def create_new_manager(self):
        # get the organization
        organizations = self.get_resource('organizations')
        self.assertIn('organizations', organizations)
        self.assertEqual(len(organizations['organizations']), 1)
        organization_id = organizations['organizations'][0]['id']

        # get the manager
        manager_id = self.get_resource('managers', expected_code=200)['managers'][0]['id']

        # get a user who is not already a manager
        all_users = self.get_resource('users', expected_code=200)['users']
        user_id = next(filter(lambda user: user['id'] != manager_id, all_users))['id']

        new_mgr = dict(id=user_id, organization_id=organization_id)
        response = self.post_resource('managers', new_mgr)
        self.assertIn('manager', response)
        return response['manager']

    def test_post_one(self):
        new_mgr = self.create_new_manager()

    def test_delete_one_manager(self):
        new_mgr = self.create_new_manager()
