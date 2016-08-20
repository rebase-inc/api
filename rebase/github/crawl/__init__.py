from collections import Iterable
from functools import partial
from logging import getLogger
from os.path import exists, join
from pickle import load

from redis import StrictRedis
from rq.job import Job

from rebase.common.debug import pdebug
from rebase.datetime import utcnow_timestamp
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
class Queues(object): pass
ALL_QUEUES = Queues()
setup_rq(ALL_QUEUES)
RQ_DEFAULT = ALL_QUEUES.default_queue


def scan(user_or_users):
    if isinstance(user_or_users, str):
        github_users = tuple([user_or_users])
    elif isinstance(user_or_users, Iterable):
        github_users = tuple(user_or_users)
    else:
        raise TypeError('user_or_users must be either a "str" for a single user, or an Iterable for many')
    batch_id = hash( (hash(github_users), utcnow_timestamp()) )
    for user_login in github_users:
        RQ_DEFAULT.enqueue_call(
            func='rebase.github.crawl.jobs.scan_user',
            args=(user_login, batch_id),
            timeout=7200
        )
    return batch_id


def read(user):
    '''
        'user' is the Github login.
        Returns a dictionary with the following keys: ['unknown_extension_counter', 'technologies', 'commit_count_by_language'].
    '''
    user_dir = '/crawler/{}'.format(user)
    public_data = join(user_dir, 'data')
    private_data = join(user_dir, 'private')
    path = private_data if exists(private_data) else public_data
    with open(path, 'rb') as f:
        return load(f)

