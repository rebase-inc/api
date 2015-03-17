from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestGithubAccountResource(AlveareRestTestCase):
    def setUp(self):
        self.github_account_resource = AlveareResource(self, 'GithubAccount')
        super().setUp()

    def test_get_one(self):
        account = self.github_account_resource.get_any()
        self.assertTrue(account) # mock should have created at least one account
        self.assertTrue(account['user_name'])
        self.assertTrue(account['remote_work_history'])

    def test_delete(self):
        self.github_account_resource.delete_any()

    def test_delete_remote_work_history(self):
        account = self.github_account_resource.get_any()
        account_url = self.github_account_resource.url(account)
        rwh_id = account['remote_work_history']['id']
        self.delete_resource('remote_work_histories/{}'.format(rwh_id))
        self.get_resource(account_url, 404)

    def test_delete_contractor(self):
        account = self.github_account_resource.get_any()
        account_url = self.github_account_resource.url(account)
        self.delete_resource('contractors/{id}'.format(**account['remote_work_history']))
        self.get_resource(account_url, 404)

    def test_create(self):
        account = self.github_account_resource.get_any()
        rwh_id = account['remote_work_history']['id']
        new_account = self.github_account_resource.create(
            remote_work_history=dict(id=rwh_id),
            user_name='george_washington',
            auth_token='1234123415245353543'
        ) 

    def test_update(self):
        account = self.github_account_resource.get_any()
        account['user_name'] = 'XXXXX'
        account['auth_token'] = 'ZZZZZ'
        self.github_account_resource.update(**account) 
