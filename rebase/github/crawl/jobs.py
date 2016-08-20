from atexit import register
from contextlib import contextmanager
from logging import getLogger
from os import makedirs, environ
from os.path import isdir, join
from pickle import dump

from github import Github

from rebase.app import basic_app
from rebase.common.debug import pdebug
from rebase.features.logger import setup_logger
from ..account_scanner import scan_one_user


logger = getLogger(__name__)




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
    global CRAWLER_USERNAME
    CRAWLER_USERNAME = conf['CRAWLER_USERNAME']
    global CRAWLER_AUTHORIZATION
    CRAWLER_AUTHORIZATION = authorization


class NotAuthorizedYet(Exception):

    def __init__(self):
        super().__init__('You need to call rebase.github.crawl.create_personal_access_token first before you can scan a Github user')


def scan_user(user_login, batch_id=None):
    if 'CRAWLER_AUTHORIZATION' not in globals():
        raise NotAuthorizedYet()
    scan_one_user(CRAWLER_AUTHORIZATION.token, CRAWLER_USERNAME, user_login)



