from requests import get

from rebase.common.database import DB
from rebase.common.exceptions import InvalidGithubAccessToken
from rebase.github import create_github_apps
from rebase.models import (
    GithubAccount,
    User,
)

class GithubSession(object):
    def __init__(self, app, api, account, user):
        self.app = app
        self.api = api
        self.account = account
        self.user = user
        self.verify()

    def __hash__(self):
        return hash('{account_id}_{user_id}'.format(
            account_id=self.account.id, 
            user_id=self.user.id
        ))

    def verify(self):
        '''
        If the access_token for this account is no longer valid, verify will:
        1/ delete the GithubAccount for this user
        2/ raise rebase.common.exceptions.InvalidGithubAccessToken
        Otherwise it will return immediately.
        '''
        response = get(
            self.api.base_url+'applications/{client_id}/tokens/{access_token}'.format(
                client_id=self.api.consumer_key,
                access_token=self.account.access_token
            ),
            auth=(self.api.consumer_key, self.api.consumer_secret)
        )
        if response.status_code != 200:
            DB.session.delete(self.account)
            DB.session.commit()
            raise InvalidGithubAccessToken(self.user, self.account.login)


def make_session(github_account, app, user):
    github = create_github_apps(app)[github_account.product]
    @github.tokengetter
    def get_github_oauth_token():
        return (github_account.access_token, '')
    return GithubSession(app, github, github_account, user)


def create_admin_github_session(account_id):
    ''' you MUST call 'destroy_session' when you are using the session returned by 'create_admin_github_session'
    '''
    from rebase.app import create
    app = create()
    app_context = app.app_context()
    app_context.push()
    user = User('RQ', 'RQ', 'RQ')
    user.admin = True
    github_account = GithubAccount.query.filter(GithubAccount.id==account_id).first()
    if not github_account:
        raise RuntimeError('Could not find a GithubAccount with id \'{}\''.format(account_id))
    return make_session(github_account, app, user), app_context

