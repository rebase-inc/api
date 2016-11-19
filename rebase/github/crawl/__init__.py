from collections import Iterable
from logging import getLogger

from ...datetime import utcnow_timestamp
from ...features.rq import DEFAULT


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


def scan(user_or_users):
    if isinstance(user_or_users, str):
        github_users = tuple([user_or_users])
    elif isinstance(user_or_users, Iterable):
        github_users = tuple(user_or_users)
    else:
        raise TypeError('user_or_users must be either a "str" for a single user, or an Iterable for many')
    batch_id = hash( (hash(github_users), utcnow_timestamp()) )
    for user_login in github_users:
        DEFAULT.enqueue_call(
            func='rebase.github.crawl.jobs.scan_user',
            args=(user_login, batch_id),
            timeout=7200
        )
    return batch_id


def update_user_rankings(user):
    return DEFAULT.enqueue_call(
        func='rebase.db_jobs.contractor.update_user_rankings',
        args=(user,),
        timeout= 300
    )


