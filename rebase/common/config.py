from os import environ

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
    if 'GITHUB_CLIENT_ID' not in environ:
        raise KeyError('Missing GITHUB_CLIENT_ID from environment. Please follow README.md instructions.')
    GITHUB_CLIENT_ID = environ['GITHUB_CLIENT_ID']
    if 'GITHUB_CLIENT_SECRET' not in environ:
        raise KeyError('Missing GITHUB_CLIENT_SECRET from environment. Please follow README.md instructions.')
    GITHUB_CLIENT_SECRET = environ['GITHUB_CLIENT_SECRET']


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestingConfig(Config):
    TESTING = True
