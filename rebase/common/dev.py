from logging import DEBUG

DEVELOPMENT = True
DEBUG = True
DEBUG_TB_INTERCEPT_REDIRECTS = False
FLASK_LOGIN_SESSION_PROTECTION = "basic"
NOMINATE_ALL_CONTRACTORS = True
NOTIFICATION_EMAIL = 'com.rebaseapp.dev@gmail.com'
NOTIFICATION_EMAIL_PASSWORD = 'eWN-pho-JTg-3mA'
BASIC_LOG_CONFIG = {
    'level':    DEBUG,
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

CRAWLER_PUBLIC_REPOS_TOKENS = {
    'Crawler 1': '553865b81fc7c79f92f854873f44e4cac71e9bae',
    'Crawler 2': '79c3c30e27c93c1b7e1051bc3f34deb17a404fb0',
    'Crawler 3': 'e71d1cfae0c037607d73bd1f9d075fac7a0d2219',
    'Crawler 4': '218e823175e4760324a21a3a847aada9b8eb5184',
}


