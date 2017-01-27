from logging import INFO
from os import environ

SECRET_KEY =                        environ['FLASK_SECRET_KEY']
PUBLIC_APP_URL =                    environ['PUBLIC_APP_URL']
API_URL_PREFIX =                    environ['API_URL_PREFIX']
REDIS_HOST =                        environ['REDIS_HOST']
GITHUB_APP_CLIENT_ID =              environ['GITHUB_APP_CLIENT_ID']
GITHUB_APP_CLIENT_SECRET =          environ['GITHUB_APP_CLIENT_SECRET']
FLASK_LOGIN_SESSION_PROTECTION =    environ['FLASK_LOGIN_SESSION_PROTECTION']
COOKIE_SECURE_HTTPPONLY =           { 'secure': True, 'httponly': False }
SQLALCHEMY_POOL_SIZE =              1
SQLALCHEMY_MAX_OVERFLOW =           1
SQLALCHEMY_TRACK_MODIFICATIONS =    False
SQLALCHEMY_DATABASE_URI =           '{dialect}://{username}:{password}@{host}/{url}'.format(
                                        dialect = 'postgres',
                                        username = 'postgres',
                                        password = '',
                                        host = environ['DATABASE_HOST'],
                                        url = 'postgres'
                                    )


############ WHAT ARE THESE FOR? #################
DEBUG =                             False
TESTING =                           False
CSRF_ENABLED =                      True
