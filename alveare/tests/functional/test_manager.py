import json
import time

from . import AlveareRestTestCase

def mgr_url(id):
    return '/managers/{}'.format(id)

class TestManagerResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('managers')
        self.assertIn('managers', response)

    def test_get_one(self):
        all_managers = self.get_resource('managers')
        self.assertEqual(len(all_managers['managers']), 1)
        manager = all_managers['managers'][0]
        url = mgr_url(manager['id'])

        response = self.get_resource(url)
        self.assertIn('manager', response)
        same_manager = response['manager']

        self.assertEqual(manager['id'], same_manager['id'])
        self.assertEqual(manager['organization_id'], same_manager['organization_id'])

    def create_new_manager(self):

        # get the manager
        manager = self.get_resource('managers')['managers'][0]
        id = manager['id']
        organization_id = manager['organization_id']

        # get a user who is not already a manager
        all_users = self.get_resource('users')['users']
        user_id = next(filter(lambda user: user['id'] != id, all_users))['id']

        new_mgr = dict(id=user_id, organization_id=organization_id)
        response = self.post_resource('managers', new_mgr)
        self.assertIn('manager', response)
        return response['manager']

    def test_post(self):
        new_mgr = self.create_new_manager()

    def test_delete(self):
        new_mgr = self.create_new_manager()
        id = new_mgr['id']
        org = new_mgr['organization_id']
        self.delete_resource(mgr_url(id))
        self.get_resource(mgr_url(id), 404)
