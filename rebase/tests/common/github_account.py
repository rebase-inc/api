from math import floor

from rebase import models
from rebase.common import mock
from rebase.models.github_account import GithubAccount
from rebase.tests.common.use_case import UseCase

class GithubAccountUseCase(UseCase):

    def user_account(self, db):
        user = mock.create_one_user(db)
        account = GithubAccount(user, 'yomama', 's3f74jg9l10fb4')

        db.session.commit()
        return user, account

    def admin_user_account(self, db):
        admin_user = mock.create_one_user(db, admin=True)
        _, account = self.user_account(db)
        return admin_user, account
