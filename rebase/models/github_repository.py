
from rebase.common.database import DB, PermissionMixin

class GithubRepository(DB.Model, PermissionMixin):
    __pluralname__ = 'github_repositories'

    id =                DB.Column(DB.Integer, primary_key=True)
    github_account_id = DB.Column(DB.Integer, DB.ForeignKey('github_account.id', ondelete='CASCADE'))
    repo_id =           DB.Column(DB.Integer, nullable=False)
    url =               DB.Column(DB.String, nullable=False)

    def __init__(self, account, repo_id, repo_url):
        self.github_account = account
        self.repo_id = repo_id
        self.url = repo_url

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return user.is_admin() or self.user == user

    def __repr__(self):
        return '<GithubRepository[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_manager_path = cls.as_contractor_path = [
            models.GithubAccount
        ]
