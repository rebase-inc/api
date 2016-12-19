from logging import INFO
from os import environ

SECRET_KEY =                        environ['FLASK_SECRET_KEY']
PUBLIC_APP_URL =                    environ['PUBLIC_APP_URL']
API_URL_PREFIX =                    environ['API_URL_PREFIX']
REDIS_HOST =                        environ['REDIS_HOST']
RSYSLOG_HOST =                      environ['RSYSLOG_HOST']
RSYSLOG_PORT =                      environ['RSYSLOG_PORT']
GITHUB_APP_CLIENT_ID =              environ['GITHUB_APP_CLIENT_ID']
GITHUB_APP_CLIENT_SECRET =          environ['GITHUB_APP_CLIENT_SECRET']
FLASK_LOGIN_SESSION_PROTECTION =    environ['FLASK_LOGIN_SESSION_PROTECTION']
ONLY_SCAN_THIS_REPO =               environ['ONLY_SCAN_THIS_REPO'] if 'ONLY_SCAN_THIS_REPO' in environ else None
COOKIE_SECURE_HTTPPONLY =           { 'secure': True, 'httponly': False }
LOG_FORMAT =                        '%(levelname)s {%(processName)s[%(process)d]} %(message).900s'
LOG_LEVEL =                         INFO
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
MAX_CONTENT_LENGTH =                1024 * 1024
