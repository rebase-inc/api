from atexit import register
from contextlib import contextmanager
from logging import getLogger
from os import makedirs, environ
from os.path import isdir, join
from pickle import dump

from github import Github

from rebase.app import basic_app
from rebase.common.debug import pdebug
from rebase.common.settings import config
from ..account_scanner import scan_one_user


logger = getLogger(__name__)


def create_personal_access_token():
    crawler_username = config['CRAWLER_USERNAME']
    crawler_password = config['CRAWLER_PASSWORD']
    logger.debug('Crawler username: %s', crawler_username)
    github = Github(
        login_or_token=crawler_username,
        password=crawler_password
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
    CRAWLER_USERNAME = crawler_username
    global CRAWLER_AUTHORIZATION
    CRAWLER_AUTHORIZATION = authorization


class NotAuthorizedYet(Exception):

    def __init__(self):
        super().__init__('You need to call rebase.github.crawl.create_personal_access_token first before you can scan a Github user')


def scan_user(user_login, batch_id=None):
    if 'CRAWLER_AUTHORIZATION' not in globals():
        raise NotAuthorizedYet()
    scan_one_user(CRAWLER_AUTHORIZATION.token, CRAWLER_USERNAME, user_login)



