from requests import get

from rebase.common.exceptions import InvalidGithubAccessToken
from rebase.github import create_github_app
from rebase.models import (
    GithubAccount,
    User,
)

class GithubSession(object):
    def __init__(self, api, account, user, DB):
        self.api = api
        self.account = account
        self.user = user
        self.DB = DB
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
            self.DB.session.delete(self.account)
            self.DB.session.commit()
            raise InvalidGithubAccessToken(self.user, self.account.login)


def make_session(github_account, app, user, db):
    github = create_github_app(app)
    @github.tokengetter
    def get_github_oauth_token():
        return (github_account.access_token, '')
    return GithubSession(github, github_account, user, db)

def make_admin_github_session(account_id):
    from rebase.app import create
    app, _, db = create()
    user = User('RQ', 'RQ', 'RQ')
    user.admin = True
    github_account = GithubAccount.query.filter(GithubAccount.id==account_id).first()
    if not github_account:
        raise RuntimeError('Could not find a GithubAccount with id \'{}\''.format(account_id))
    return make_session(github_account, app, user, db)

