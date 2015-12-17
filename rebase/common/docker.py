from rebase.common.config import DevelopmentConfig

class Dev(DevelopmentConfig):
    WORK_REPOS_HOST = 'git_1'
    UPLOAD_FOLDER = '/uploads'
    SECRET_KEY = "\x86\xa1\xb8\xfbP\x8f\xd6\x1c'\xad-\xdb\xf8+K=\x820g<5\x16|l"
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:@db/postgres'
    GITHUB_CLIENT_ID = 'ccfe7b7be7560c9a112e'
    GITHUB_CLIENT_SECRET = '1779c1d363dec567c81c01ef266e4d3f30f79a8d'
