from logging import DEBUG as DEBUG_LEVEL

DEVELOPMENT = True
DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
FLASK_LOGIN_SESSION_PROTECTION = "basic"
NOMINATE_ALL_CONTRACTORS = True
NOTIFICATION_EMAIL = 'com.rebaseapp.dev@gmail.com'
NOTIFICATION_EMAIL_PASSWORD = 'eWN-pho-JTg-3mA'
BASIC_LOG_CONFIG = {
    'level':    DEBUG_LEVEL,
    'format':   '%(levelname)s {%(processName)s[%(process)d]} %(message)s',
}

SECRET_KEY = "\x86\xa1\xb8\xfbP\x8f\xd6\x1c'\xad-\xdb\xf8+K=\x820g<5\x16|l"
COOKIE_SECURE_HTTPPONLY = { 'secure': False, 'httponly': False }
GIT_SERVER_URL_PREFIX='ssh://git@dev:2222/'


