from datetime import timedelta
from logging import INFO
from os import environ


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
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
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:@database/postgres'
    WORK_REPOS_HOST = 'rq_git'
    WORK_REPOS_ROOT = '/git'
    SSH_AUTHORIZED_KEYS = '/home/git/.ssh/authorized_keys'
    UPLOAD_FOLDER = '/uploads'
    REDIS_HOST = 'redis'
    CACHE_HOST = 'cache:5000'
    BASIC_LOG_CONFIG = {
        'level':    INFO,
        'format':   '%(levelname)s {%(processName)s[%(process)d]} %(message)s',
    }
    RSYSLOG_CONFIG = {
        'address': ('rsyslog', 514),
    }
    SMTP_HOST='smtp.gmail.com'
    COOKIE_SECURE_HTTPPONLY = { 'secure': True, 'httponly': False }


