from collections import Iterable
from functools import partial
from logging import getLogger
from os import environ

from github import Github
from redis import StrictRedis
from rq.job import Job

from rebase.app import basic_app
from rebase.common.debug import pdebug
from rebase.datetime import utcnow_timestamp
from rebase.features.logger import setup_logger
from rebase.features.rq import setup_rq


logger = getLogger(__name__)


# from webflow:
some_users = [
    # famous python devs:
    # Alex Gaynor (PyPy, etc.)
    #'alex',
    # Mike Bayer (SqlAlchemy)
    #'zzzeek',
    'rapha-opensource',
    #'kerseyi',
    #'alexpchin',
    #'gacpro',
    #'Eveykilel',
    #'Johnathon332',
    #'jitorrent',
    #'arunanson',
    #'MarkTJBrown',
    #'ezynda3',
    #'mgraham134',
]

# not a valid user: 'Toahniwalakshay'

def get_personal_access_token():
    # TODO simplify design by removing the need for a Flask app here
    # all we need is a configuration (partially shared with the 'real' Flask app)
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
    return authorization


class Queues(object): pass
all_queues = Queues()
setup_rq(all_queues)
rq_default = all_queues.default_queue


CRAWLER_AUTHORIZATION = get_personal_access_token()


def scan(user_or_users):
    if isinstance(user_or_users, str):
        github_users = tuple([user_or_users])
    elif isinstance(user_or_users, Iterable):
        github_users = tuple(user_or_users)
    else:
        raise TypeError('user_or_users must be either a "str" for a single user, or an Iterable for many')
    batch_id = hash( (hash(github_users), utcnow_timestamp()) )
    for user_login in github_users:
        rq_default.enqueue_call(
            func='rebase.crawl.jobs.scan_user',
            args=(user_login, CRAWLER_AUTHORIZATION.token, batch_id),
            timeout=7200
        )
    return batch_id


