from datetime import timedelta
import logging
from os import environ

from rebase.common.env import check


check([
    'REBASE_CLIENT_HOST',
    'REBASE_CLIENT_PORT',
])


SERVER_NAME = '{HOST}:{PORT}'.format(
    HOST=environ['REBASE_CLIENT_HOST'],
    PORT=environ['REBASE_CLIENT_PORT']
)


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    CLONING_SERVER_URL = 'http://ec2-52-21-89-158.compute-1.amazonaws.com:5001/'
    SQLALCHEMY_POOL_SIZE = 1
    SQLALCHEMY_MAX_OVERFLOW = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    NOMINATE_ALL_CONTRACTORS = False
    MAX_CONTENT_LENGTH = 1024 * 1024
    WORK_BRANCH_NAME = 'work_{contractor_id}_{auction_id}'.format
    REVENUE_FACTOR = 1.1 # 10 % of WorkOffer price is going to us if Work is complete
    URL_PREFIX = '/api/v1'
    FINISH_WORK_BY = timedelta(days=7)
    AUCTION_EXPIRATION = timedelta(days=3)
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:@db/postgres'
    GIT_SERVER_NAME=environ['REBASE_CLIENT_HOST']
    WORK_REPOS_HOST = 'rq_git_1'
    WORK_REPOS_ROOT = '/git'
    SSH_AUTHORIZED_KEYS = '/home/git/.ssh/authorized_keys'
    UPLOAD_FOLDER = '/uploads'
    REDIS_HOST = 'redis_1'
    CACHE_HOST = 'cache_1:5000'
    BASIC_LOG_CONFIG = {
        'level':    logging.DEBUG,
        'format':   '%(levelname)s {%(processName)s[%(process)d] %(threadName)s} %(message)s',
    }
    RSYSLOG_CONFIG = {
        'address': ('rsyslog', 514),
    }
    SMTP_HOST='smtp.gmail.com'


