from os import environ

from rebase.common.env import check

check([
    'SECRET_KEY',
    'NOTIFICATION_EMAIL_PASSWORD',
])

NOMINATE_ALL_CONTRACTORS = True
NOTIFICATION_EMAIL = 'com.rebaseapp.alpha'
NOTIFICATION_EMAIL_PASSWORD = environ['NOTIFICATION_EMAIL_PASSWORD']

FLASK_LOGIN_SESSION_PROTECTION = "strong" # WARNING: this will make Apache Bench fail login unless it is used to login as well
SECRET_KEY = environ['SECRET_KEY']

GIT_SERVER_URL_PREFIX='git@alpha.rebaseapp.com:'


