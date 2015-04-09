import json
import time

from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource

def mgr_url(id):
    return '/managers/{}'.format(id)

class TestManagerResource(AlveareRestTestCase):
    def setUp(self):
        self.manager_resource = AlveareResource(self, 'Manager')
        super().setUp()

    def test_get_all_as_admin(self):
        self.login_admin()
        self.assertTrue(self.manager_resource.get_all())

    def test_get_all_as_manager(self):
        user = self.login_as_manager_only()
        managers = self.manager_resource.get_all()
        self.assertTrue(managers)
        for manager in managers:
            self.assertIn('user', manager)
            self.assertIn('id', manager['user'])
            self.assertEqual(manager['user']['id'], user.id)

    def test_get_all_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        managers = self.manager_resource.get_all()
        self.assertTrue(managers)
        for manager in managers:
            print(manager)
            self.assertIn('organization', manager)

    def _get_one(self):
        all_managers = self.get_resource('managers')
        self.assertIsInstance(all_managers['managers'], list)
        manager = all_managers['managers'][0]
        url = mgr_url(manager['id'])

        response = self.get_resource(url)
        self.assertIn('manager', response)
        same_manager = response['manager']

        self.assertEqual(manager['id'], same_manager['id'])
        self.assertEqual(manager['organization']['id'], same_manager['organization']['id'])

    def test_get_one_as_admin(self):
        self.login_admin()
        self._get_one()

    def test_get_one_as_manager(self):
        self.login_as_manager_only()
        self._get_one()

    def test_get_one_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        self._get_one()

    def create_new_manager(self):

        # get the manager
        manager = self.get_resource('managers')['managers'][0]
        id = manager['id']
        organization = dict(id = manager['organization']['id'])

        # get a user who is not already a manager
        all_users = self.get_resource('users')['users']
        user_id = next(filter(lambda user: user['id'] != id, all_users))['id']

        new_mgr = dict(user=dict(id=user_id), organization=organization)
        response = self.post_resource('managers', new_mgr)
        self.assertIn('manager', response)
        return response['manager']

    def test_post(self):
        self.login_admin()
        new_mgr = self.create_new_manager()

    def test_delete(self):
        self.login_admin()
        new_mgr = self.create_new_manager()
        id = new_mgr['id']
        org = new_mgr['organization']
        self.delete_resource(mgr_url(id))
        self.get_resource(mgr_url(id), 404)
