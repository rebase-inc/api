
class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    CLONING_SERVER_URL = 'http://ec2-52-21-89-158.compute-1.amazonaws.com:5001/'
    SQLALCHEMY_POOL_SIZE = 1
    SQLALCHEMY_MAX_OVERFLOW = 1
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    NOMINATE_ALL_CONTRACTORS = False
    LOG_FILE = '/tmp/rebase_web.log'
    MAX_CONTENT_LENGTH = 1024 * 1024
    TMP_KEYS = '/tmp/authorized_keys'
    TMP_AUTHORIZED_USERS = '/tmp/authorized_users'
    SSH_AUTHORIZED_KEYS = '.ssh/authorized_keys2'
    WORK_BRANCH_NAME = 'work_{contractor_id}_{auction_id}'.format
    REVENUE_FACTOR = 1.1 # 10 % of WorkOffer price is going to us if Work is complete
    URL_PREFIX = '/api/v1'


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
