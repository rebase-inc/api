
from . import RebaseRestTestCase, PermissionTestCase
from rebase.common.utils import RebaseResource, ids
from rebase.models import Contractor, RemoteWorkHistory, GithubAccount
from rebase.tests.common.github_account import GithubAccountUseCase


class TestGithubAccount(PermissionTestCase):
    model = 'GithubAccount'

    def setUp(self):
        super().setUp()
        self.case = GithubAccountUseCase()

    def validate_view(self, github_account):
        self.assertIsInstance(github_account.pop('id'), int)
        self.assertIsInstance(github_account.pop('user_name'), str)
        self.assertIsInstance(github_account.pop('oauth_token'), str)

    def update(_, github_account):
        updated_github_account = ids(github_account)
        updated_github_account.update(access_token=github_account.access_token)
        return updated_github_account

    def new(_, account):
        return {
            'user_name': account.user_name,
            'access_token': account.access_token
        }

    def test_view(self):
        user, account = self._run(self.case.user_account, 'manager')


class TestGithubAccountResource(RebaseRestTestCase):
    def setUp(self):
        self.github_account_resource = RebaseResource(self, 'GithubAccount')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        account = self.github_account_resource.get_any()
        self.assertTrue(account) # mock should have created at least one account
        self.assertTrue(account['user_name'])
        self.assertTrue(account['remote_work_history'])

    def test_delete(self):
        self.login_admin()
        self.github_account_resource.delete_any()

    def test_delete_remote_work_history(self):
        self.login_admin()
        account = self.github_account_resource.get_any()
        account_url = self.github_account_resource.url(account)
        rwh_id = account['remote_work_history']['id']
        self.delete_resource('remote_work_histories/{}'.format(rwh_id))
        self.get_resource(account_url, 404)

    def test_delete_contractor(self):
        self.login_admin()
        account = self.github_account_resource.get_any()
        account_url = self.github_account_resource.url(account)
        self.delete_resource('contractors/{id}'.format(**account['remote_work_history']))
        self.get_resource(account_url, 404)

    def test_create(self):
        self.login_admin()
        account = self.github_account_resource.get_any()
        rwh_id = account['remote_work_history']['id']
        new_account = self.github_account_resource.create(
            remote_work_history=dict(id=rwh_id),
            user_name='george_washington',
            auth_token='1234123415245353543'
        )

    def test_update(self):
        self.login_admin()
        account = self.github_account_resource.get_any()
        account['user_name'] = 'XXXXX'
        account['auth_token'] = 'ZZZZZ'
        self.github_account_resource.update(**account)

    def test_allowed_to_be_created_by_contractor_user(self):
        contractor = Contractor.query.filter(~Contractor.remote_work_history.has()).first()
        rwh = RemoteWorkHistory(contractor)
        self.db.session.add(rwh)
        self.db.session.commit()
        self.post_resource('github_accounts', dict(user_name='foobar', remote_work_history=dict(id=rwh.id), auth_token='asdf'), 401)
        self.login(contractor.user.email, 'foo')
        self.post_resource('github_accounts', dict(user_name='foobar', remote_work_history=dict(id=rwh.id), auth_token='asdf'))

    def test_allowed_to_be_deleted_by_contractor_user(self):
        contractor = Contractor.query.filter(~Contractor.remote_work_history.has()).first()
        rwh = RemoteWorkHistory(contractor)
        gh_account = GithubAccount(rwh, 'foobar')
        self.db.session.add(gh_account)
        self.db.session.commit()
        self.delete_resource('github_accounts/{}'.format(gh_account.id), 401)
        self.login(contractor.user.email, 'foo')
        self.delete_resource('github_accounts/{}'.format(gh_account.id))

    def test_that_contractor_only_sees_their_github_accounts(self):
        contractor = Contractor.query.filter(~Contractor.remote_work_history.has()).first()
        rwh = RemoteWorkHistory(contractor)
        gh_account = GithubAccount(rwh, 'foobar')
        self.db.session.add(gh_account)
        self.db.session.commit()

        self.login(contractor.user.email, 'foo')
        github_accounts = self.get_resource('github_accounts')['github_accounts']
        github_account_ids = [github_account['id'] for github_account in github_accounts]
        self.assertEqual([gh_account.id], github_account_ids)

