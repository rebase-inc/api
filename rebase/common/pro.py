from os import environ

from rebase.common.env import check

check([
    'SECRET_KEY',
    'GITHUB_APP_SECRET',
    'GITHUB_CODE2RESUME_SECRET',
    'NOTIFICATION_EMAIL_PASSWORD',
])

NOTIFICATION_EMAIL = 'com.rebaseapp.alpha'
NOTIFICATION_EMAIL_PASSWORD = environ['NOTIFICATION_EMAIL_PASSWORD']

FLASK_LOGIN_SESSION_PROTECTION = "strong" # WARNING: this will make Apache Bench fail login unless it is used to login as well
SECRET_KEY = environ['SECRET_KEY']

GITHUB_APP_ID = '78a6f5326fe65be4fb21'
GITHUB_APP_SECRET = environ['GITHUB_APP_SECRET']
GITHUB_CODE2RESUME_ID = '93bc2584d7e443514e7c'
GITHUB_CODE2RESUME_SECRET = environ['GITHUB_CODE2RESUME_SECRET']

GIT_SERVER_NAME='app.rebaseapp.com'
APP_URL='https://app.rebaseapp.com'
CODE2RESUME_URL='https://code2resume.rebaseapp.com'
