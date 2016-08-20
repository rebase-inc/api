from atexit import register
from contextlib import contextmanager
from logging import getLogger
from os import makedirs, environ
from os.path import isdir, join
from pickle import dump

from github import Github

from rebase.app import basic_app
from rebase.common.debug import pdebug
from rebase.common.stopwatch import InfoElapsedTime
from rebase.features.logger import setup_logger
from ..account_scanner import AccountScanner


logger = getLogger(__name__)


DATA_ROOT = '/crawler'


def create_personal_access_token(app=None):
    # TODO simplify design by removing the need for a Flask app here
    # all we need is a configuration (partially shared with the 'real' Flask app)
    if not app:
        app = basic_app()
    setup_logger(app)
    conf = app.config
    github = Github(
        login_or_token=conf['CRAWLER_USERNAME'],
        password=conf['CRAWLER_PASSWORD']
    )
    fingerprint = environ['HOSTNAME']
    user = github.get_user()
    logger.debug('Authenticated Github user: %s', user.login)
    authorizations = user.get_authorizations()
    authorization = None
    for auth in authorizations:
        if auth.note == fingerprint:
            authorization = auth
    if authorization:
        authorization.delete()
    authorization = user.create_authorization(
        scopes=['public_repo'],
        note=fingerprint,
        onetime_password=fingerprint
    )
    register(authorization.delete)
    global CRAWLER_AUTHORIZATION
    CRAWLER_AUTHORIZATION = authorization


class NotAuthorizedYet(Exception):

    def __init__(self):
        super().__init__('You need to call rebase.github.crawl.create_personal_access_token first before you can scan a Github user')


def scan_user(user_login, batch_id=None):
    if 'CRAWLER_AUTHORIZATION' not in globals():
        raise NotAuthorizedYet()
    token = CRAWLER_AUTHORIZATION.token
    logger.debug('scan_user: [%s, %s, %s]', user_login, token, batch_id)
    user_data = dict()
    start_msg = 'processing Github user: '+user_login
    try:
        with InfoElapsedTime(start=start_msg, stop=start_msg+' took %f seconds'):
            commit_count_by_language, unknown_extension_counter, technologies = AccountScanner(
                token,
                'rebase-dev'
            ).scan_all_repos(login=user_login)
        user_data['commit_count_by_language'] = commit_count_by_language
        user_data['technologies'] = technologies
        user_data['unknown_extension_counter'] = unknown_extension_counter
        user_data_dir = join(DATA_ROOT, user_login)
        user_data_path = join(user_data_dir, 'data')
        if not isdir(user_data_dir):
            makedirs(user_data_dir)
        with open(user_data_path, 'wb') as f:
            dump(user_data, f)
        return 'success'
    except TimeoutError as timeout_error:
        return str(timeout_error)


