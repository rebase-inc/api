from os import environ, path

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = environ['FLASK_SECRET_KEY']
    SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
    if 'GITHUB_CLIENT_ID' not in environ:
        raise KeyError('Missing GITHUB_CLIENT_ID from environment. Please follow README.md instructions.')
    GITHUB_CLIENT_ID = environ['GITHUB_CLIENT_ID']
    if 'GITHUB_CLIENT_SECRET' not in environ:
        raise KeyError('Missing GITHUB_CLIENT_SECRET from environment. Please follow README.md instructions.')
    GITHUB_CLIENT_SECRET = environ['GITHUB_CLIENT_SECRET']
    CLONING_SERVER_URL = 'http://ec2-52-21-89-158.compute-1.amazonaws.com:5001/'
    SQLALCHEMY_POOL_SIZE = int(environ['CONNECTION_POOL_SIZE_PER_WORKER'])
    SQLALCHEMY_MAX_OVERFLOW = 1
    NOMINATE_ALL_CONTRACTORS = False
    LOG_FILE = '/tmp/rebase_web.log'
    UPLOAD_FOLDER = path.expanduser('~/uploads/')
    MAX_CONTENT_LENGTH = 1024 * 1024
    WORK_REPOS_HOST = 'ec2-52-21-45-203.compute-1.amazonaws.com'
    WORK_REPOS_ROOT = '/git'
    TMP_KEYS = '/tmp/authorized_keys'
    TMP_AUTHORIZED_USERS = '/tmp/authorized_users'
    SSH_AUTHORIZED_KEYS = '.ssh/authorized_keys2'
    WORK_BRANCH_NAME = 'work_{contractor_id}_{work_id}'.format
    REVENUE_FACTOR = 1.1 # 10 % of WorkOffer price is going to us if Work is complete


class ProductionConfig(Config):
    DEBUG = False
    FLASK_LOGIN_SESSION_PROTECTION = "strong" # WARNING: this will make Apache Bench fail login unless it is used to login as well


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    FLASK_LOGIN_SESSION_PROTECTION = "basic"


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    FLASK_LOGIN_SESSION_PROTECTION = "basic"
    NOMINATE_ALL_CONTRACTORS = True
    SEND_FILE_MAX_AGE_DEFAULT = 0


class TestingConfig(Config):
    TESTING = True
    FLASK_LOGIN_SESSION_PROTECTION = "basic"
