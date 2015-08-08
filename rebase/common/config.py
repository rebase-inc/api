from os import environ

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = environ['DATABASE_URL']
    HEROKU_CLIENT_ID = ''
    HEROKU_CLIENT_SECRET = ''


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    HEROKU_CLIENT_ID = 'ccfe7b7be7560c9a112e'
    HEROKU_CLIENT_SECRET = '1779c1d363dec567c81c01ef266e4d3f30f79a8d'


class TestingConfig(Config):
    TESTING = True
