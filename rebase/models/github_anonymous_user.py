from logging import getLogger

from rebase.common.database import DB
from rebase.models import User


logger = getLogger()


class GithubAnonymousUser(User):
    __pluralname__ = 'anonymous_users'

    id =                DB.Column(DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    github_user_id =    DB.Column(DB.Integer, DB.ForeignKey('github_user.id', ondelete='CASCADE'), nullable=False)

    __mapper_args__ = { 'polymorphic_identity': 'github_anonymous_user' }

    def __init__(self, github_user):
        self.github_user = github_user
        email = '__{}@dummy.email.com'.format(github_user.login)
        password = 'foo'
        super().__init__(github_user.name, email, password)

    def allowed_to_be_created_by(self, user):
        return user.admin

    def allowed_to_be_deleted_by(self, user):
        return user.admin

    def allowed_to_be_viewed_by(self, user):
        return True


