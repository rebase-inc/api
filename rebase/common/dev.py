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
GITHUB_APP_ID = 'ccfe7b7be7560c9a112e'
GITHUB_APP_SECRET = '1779c1d363dec567c81c01ef266e4d3f30f79a8d'
GITHUB_CODE2RESUME_ID = '215657378a75ef37b93e'
GITHUB_CODE2RESUME_SECRET = 'faa6edb95cfc81616604f21cad2be491beefbe50'
COOKIE_SECURE_HTTPPONLY = { 'secure': False, 'httponly': False }
GIT_SERVER_URL_PREFIX='ssh://git@dev:2222/'
APP_URL='http://dev:3000'
CODE2RESUME_URL='http://c2r:3001'

# TODO: revisit config design
# we need:
# - a 'mode' level ('dev', 'pro', 'test', 'deployment_testing', etc.)
# - a system-wide set of config params (common to all components or containers)
# - a component level set of config params

# these 2 are only for 'rq_default' crawling jobs
CRAWLER_USERNAME = 'rebase-dev'
CRAWLER_PASSWORD = '7Du-V2U-xKt-gK6'


