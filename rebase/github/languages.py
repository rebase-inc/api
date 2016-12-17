from base64 import b64decode
from logging import getLogger
from os.path import join, isdir

from rebase.common.database import DB
from .account_scanner import scan_one_user
from rebase.github.session import create_admin_github_session
from rebase.models import (
    Contractor,
    SkillSet,
)


logger = getLogger(__name__)

from flask_oauthlib.client import OAuth


OAUTH_SETTINGS = {
    'request_token_params': {'scope': 'user, repo'},
    'base_url': 'https://api.github.com/',
    'request_token_url': None,
    'access_token_method': 'POST',
    'access_token_url': 'https://github.com/login/oauth/access_token',
    'authorize_url': 'https://github.com/login/oauth/authorize'
}
def make_session(github_account, app, user):
    github = oauth_app_from_github_account(apps(app), github_account)
    @github.tokengetter
    def get_github_oauth_token():
        return (github_account.access_token, '')
    return GithubSession(app, github, github_account, user)



def scan_all_repos(github_username):
    oauth_app = OAuth(app).remote_app('github',
            consumer_key = app.config.GITHUB_APP_CLIENT_ID,
            consumer_secret = app.config.GITHUB_APP_CLIENT_SECRET,
            **OAUTH_SETTINGS
    )
    scanner = AccountScanner(github_username, github_token)
    scanner.scan_all_repos()
    scanner.close_connection()





def scan_public_and_private_repos(account_id):
    # remember, we MUST pop this 'context' when we are done with this session
    github_session, context = create_admin_github_session(account_id)
    account = github_session.account
    contractor = next(filter(lambda r: r.type == 'contractor', account.user.roles), None) or Contractor(github_session.acccount.user)
    user_data = scan_one_user(account.access_token, account.github_user.login, contractor_id=contractor.id)
    contractor.skill_set.skills = user_data['rankings']
    account.remote_work_history.analyzing = False
    DB.session.commit()
    logger.info(contractor.skill_set.skills, '{} Skills'.format(contractor))
    for extension, count in user_data['unknown_extension_counter'].most_common():
        logger.warning('Unrecognized extension "{}" ({} occurrences)'.format(extension, count))
    # popping the context will close the current database connection.
    context.pop()


