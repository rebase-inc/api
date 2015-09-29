
from rebase.common.database import DB, PermissionMixin
from rebase.models import CodeRepository

class GithubRepository(CodeRepository):
    __pluralname__ = 'github_repositories'

    id =            DB.Column(DB.Integer, DB.ForeignKey('code_repository.id', ondelete='CASCADE'), primary_key=True)
    name =          DB.Column(DB.String, nullable=False)
    repo_id =       DB.Column(DB.Integer, nullable=False, unique=True)
    description =   DB.Column(DB.String, nullable=True)

    __mapper_args__ = { 'polymorphic_identity': 'github_repository' }

    def __init__(self, project, name, repo_id, repo_url, description):
        self.name = name
        self.repo_id = repo_id
        self.description = description
        super().__init__(project, repo_url)

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
        # TODO fix as_contractor_path for permissions
        cls.as_contractor_path = [
            models.Project,
            models.Organization,
            models.Manager
        ]
        cls.as_manager_path = [
            models.Project,
            models.Organization,
            models.Manager
        ]
