
from rebase.models.user import User
from rebase.common.database import DB

class GithubUser(User):
    __pluralname__ = 'github_users'

    id =        DB.Column(DB.Integer, DB.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
    github_id = DB.Column(DB.Integer, unique=True)
    login =     DB.Column(DB.String, unique=True)

    __mapper_args__ = { 'polymorphic_identity': 'github_user' }

    def __init__(self, github_id, login, name):
        self.github_id = github_id
        self.login = login
        super().__init__(
            name,
            '__github_user_{id}_{login}@joinrebase.com'.format(
                id=self.github_id,
                login=self.login
            ),
            ''
        )

    def __repr__(self):
        return '<GithubUser[{}] {}>'.format(self.id, self.name)

    def allowed_to_be_created_by(self, user):
        return user.admin

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True

    @classmethod
    def setup_queries(cls, models):
        cls.filter_based_on_current_role = False
        cls.as_manager_path = cls.as_owner_path = cls.as_contractor_path = []
