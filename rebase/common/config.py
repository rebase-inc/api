from os import environ

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


class TestingConfig(Config):
    TESTING = True
    FLASK_LOGIN_SESSION_PROTECTION = "basic"
