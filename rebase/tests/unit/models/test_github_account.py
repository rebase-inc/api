import unittest

from . import RebaseModelTestCase
from rebase.models import Contractor, RemoteWorkHistory, GithubAccount
from rebase.common.utils import validate_query_fn
from rebase.tests.common.github_account import GithubAccountUseCase

class TestGithubAccount(RebaseModelTestCase):

    def setUp(self):
        self.case = GithubAccountUseCase()
        super().setUp()

    def test_mgr(self):
        validate_query_fn(
            self,
            GithubAccount,
            self.case.user_account,
            GithubAccount.query_by_user,
            'manager',
            False, False, False, True
        )

    def test_contractor(self):
        validate_query_fn(
            self,
            GithubAccount,
            self.case.user_account,
            GithubAccount.query_by_user,
            'contractor',
            False, False, False, True
        )

    def test_admin(self):
        validate_query_fn(
            self,
            GithubAccount,
            self.case.admin_user_account,
            GithubAccount.query_by_user,
            'contractor',
            True, True, True, True
        )
