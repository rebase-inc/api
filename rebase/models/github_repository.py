
from rebase.common.database import DB, PermissionMixin

class GithubRepository(DB.Model, PermissionMixin):
    __pluralname__ = 'github_repositories'

    id =            DB.Column(DB.Integer, primary_key=True)
    account_id =    DB.Column(DB.Integer, DB.ForeignKey('github_account.id', ondelete='CASCADE'), nullable=True)
    org_id =        DB.Column(DB.Integer, DB.ForeignKey('github_organization.id', ondelete='CASCADE'), nullable=True)
    name =          DB.Column(DB.String, nullable=False)
    repo_id =       DB.Column(DB.Integer, nullable=False, unique=True)
    url =           DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=True)

    def __init__(self, name, repo_id, repo_url, description=None, account=None, org=None):
        self.name = name
        self.repo_id = repo_id
        self.url = repo_url
        self.description = description
        if account and org:
            raise ValueError('Pick either an account or an org as the owner of this repo')
        if not account and not org:
            raise ValueError('There must be an owner for this repo, either a Github user or an organization')
        self.account = account
        self.org = org

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        if hasattr(self, 'account'):
            return self.account.user == user
        if hasattr(self, 'org'):
            return self.org.account.user == user

    def __repr__(self):
        return '<GithubRepository[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        cls.as_manager_path = cls.as_contractor_path = [
            models.GithubAccount
        ]
