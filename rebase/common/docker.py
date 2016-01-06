from os import environ

from rebase.common.env import check

check([
    'REBASE_CLIENT_HOST',
    'REBASE_CLIENT_PORT',
])

SERVER_NAME = '{HOST}:{PORT}'.format(
    HOST=environ['REBASE_CLIENT_HOST'],
    PORT=environ['REBASE_CLIENT_PORT']
)

WORK_REPOS_HOST = 'rq_git_1'
WORK_REPOS_ROOT = '/git'
UPLOAD_FOLDER = '/uploads'
SECRET_KEY = "\x86\xa1\xb8\xfbP\x8f\xd6\x1c'\xad-\xdb\xf8+K=\x820g<5\x16|l"
SQLALCHEMY_DATABASE_URI = 'postgres://postgres:@db/postgres'
GITHUB_CLIENT_ID = 'ccfe7b7be7560c9a112e'
GITHUB_CLIENT_SECRET = '1779c1d363dec567c81c01ef266e4d3f30f79a8d'
