from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestGithubAccountResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'GithubAccount')
        super().setUp()

    def test_get_one(self):
        account = self.r.get_any()
        self.assertTrue(account) # mock should have created at least one account
        self.assertTrue(account['user_name'])
        self.assertTrue(account['remote_work_history_id'])

    def test_delete(self):
        self.r.delete_any()

    def test_delete_remote_work_history(self):
        account = self.r.get_any()
        account_url = self.r.url(account)
        rwh_id = account['remote_work_history_id']
        self.delete_resource('remote_work_histories/{}'.format(rwh_id))
        self.get_resource(account_url, 404)

    def test_delete_contractor(self):
        account = self.r.get_any()
        account_url = self.r.url(account)
        self.delete_resource('contractors/{}'.format(account['remote_work_history_id']))
        self.get_resource(account_url, 404)

    def test_create(self):
        account = self.r.get_any()
        rwh_id = account['remote_work_history_id']
        new_account = self.r.create(
            remote_work_history_id=rwh_id,
            user_name='george_washington',
            auth_token='1234123415245353543'
        ) 

    def test_update(self):
        account = self.r.get_any()
        account['user_name'] = 'XXXXX'
        account['auth_token'] = 'ZZZZZ'
        self.r.update(**account) 
