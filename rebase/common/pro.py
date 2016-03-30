from os import environ

from rebase.common.env import check

check([
    'SECRET_KEY',
    'GITHUB_CLIENT_SECRET',
])

NOTIFICATION_EMAIL = 'com.rebaseapp.alpha@gmail.com'
NOTIFICATION_EMAIL_PASSWORD = 'JgQ-b9q-en2-B7g'
FLASK_LOGIN_SESSION_PROTECTION = "strong" # WARNING: this will make Apache Bench fail login unless it is used to login as well
SECRET_KEY = environ['SECRET_KEY']
GITHUB_CLIENT_ID = '78a6f5326fe65be4fb21'
GITHUB_CLIENT_SECRET = environ['GITHUB_CLIENT_SECRET']
