from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from alveare.models import Contractor
from unittest import skip


class TestRemoteWorkHistoryResource(AlveareRestTestCase):
    def setUp(self):
        self.remote_work_history_resource = AlveareResource(self, 'RemoteWorkHistory')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        rwh = self.remote_work_history_resource.get_any()
        self.assertTrue(rwh) # mock should have created at least one account
        self.assertTrue(rwh['id'])

        contractor = self.get_resource('contractors/{id}'.format(**rwh))['contractor']
        self.assertEqual(contractor['remote_work_history']['id'], contractor['id'])

    def test_create(self):
        self.login_admin()
        contractor = AlveareResource(self, 'Contractor').get_any()
        response = self.post_resource('remote_work_histories', dict(contractor=contractor))
        new_rwh = response['remote_work_history']
        self.assertEqual(new_rwh['id'], contractor['id'])

    def test_delete(self):
        self.login_admin()
        self.remote_work_history_resource.delete_any()

    def test_delete_contractor(self):
        self.login_admin()
        rwh = self.remote_work_history_resource.get_any()
        self.delete_resource('contractors/{}'.format(rwh['id']))
        self.get_resource(self.remote_work_history_resource.url(rwh), 404)

    def test_add_and_remove_accounts(self):
        self.login_admin()
        rwh = self.remote_work_history_resource.get_any()
        rwh_id = rwh['id']
        new_account = AlveareResource(self, 'GithubAccount').create(
            remote_work_history = dict(id=rwh_id),
            user_name='george_washington',
            auth_token='1234123415245353543'
        )
        modified_rwh = self.get_resource('remote_work_histories/{}'.format(rwh_id))['remote_work_history']

        account_ids = list(map(lambda account: account['id'], modified_rwh['github_accounts']))
        self.assertIn(new_account['id'], account_ids)

        # now delete all the accounts and verify the rwh is still there
        for account_id in account_ids:
            self.delete_resource('github_accounts/{}'.format(account_id))
        queried_rwh = self.remote_work_history_resource.get(rwh_id)
        self.assertFalse(queried_rwh['github_accounts']) # verify all accounts have been deleted

    def test_allowed_to_be_created_by_contractor_user(self):
        contractor = Contractor.query.filter(~Contractor.remote_work_history.has()).first()
        self.post_resource('remote_work_histories', dict(contractor=dict(id=contractor.id)), 401)
        self.login(contractor.user.email, 'foo')
        self.post_resource('remote_work_histories', dict(contractor=dict(id=contractor.id)))

    def test_allowed_to_be_deleted_by_contractor_user(self):
        contractor = Contractor.query.filter(~Contractor.remote_work_history.has()).first()
        self.login(contractor.user.email, 'foo')
        self.post_resource('remote_work_histories', dict(contractor=dict(id=contractor.id)))
        self.logout()
        self.delete_resource('remote_work_histories/{}'.format(contractor.id), 401)
        self.login(contractor.user.email, 'foo')
        self.delete_resource('remote_work_histories/{}'.format(contractor.id))


