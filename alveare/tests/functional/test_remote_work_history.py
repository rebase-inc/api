from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestRemoteWorkHistoryResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'remote_work_history')
        super().setUp()

    def test_get_one(self):
        rwh = self.r.get_any()
        self.assertTrue(rwh) # mock should have created at least one account
        self.assertTrue(rwh['id'])

        contractor = self.get('contractor', rwh['id'])
        self.assertEqual(contractor['remote_work_history'], contractor['id'])

    def test_create(self):
        contractor = AlveareResource(self, 'contractor').get_any()
        new_rwh = self.r.create(
            id=contractor['id']
        )

    def test_delete(self):
        self.r.delete_any()

    def test_delete_contractor(self):
        rwh = self.r.get_any()
        self.delete_resource('contractors/{}'.format(rwh['id']))
        self.get_resource(self.r.url(rwh), 404)

    def test_add_and_remove_accounts(self):
        rwh = self.r.get_any()
        rwh_id = rwh['id']
        new_account = AlveareResource(self, 'github_account').create(
            remote_work_history_id=rwh_id,
            user_name='george_washington',
            auth_token='1234123415245353543'
        )
        modified_rwh = self.get('remote_work_history', rwh_id)

        account_ids = list(map(lambda account: account['id'], modified_rwh['github_accounts']))
        self.assertIn(new_account['id'], account_ids)

        # now delete all the accounts and verify the rwh is still there
        for account_id in account_ids:
            self.delete_resource('github_accounts/{}'.format(account_id))
        queried_rwh = self.r.get(rwh_id)
        self.assertFalse(queried_rwh['github_accounts']) # verify all accounts have been deleted
