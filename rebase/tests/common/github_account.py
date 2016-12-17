from math import floor
from random import randint

from rebase import models
from rebase.common import mock
from rebase.models.github_account import GithubAccount
from rebase.tests.common.use_case import UseCase
from rebase.common.utils import pick_an_organization_name

class GithubAccountUseCase(UseCase):

    def user_account(self, db):
        user = mock.create_one_user(db)
        account_id = randint(999, 999999)
        account = GithubAccount(user, account_id, pick_an_organization_name(), 'access_token_{}'.format(account_id))

        db.session.commit()
        return user, account

    def admin_user_account(self, db):
        admin_user = mock.create_one_user(db, admin=True)
        _, account = self.user_account(db)
        return admin_user, account
