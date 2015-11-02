
from rebase.common.database import DB, PermissionMixin
from rebase.models import CodeRepository

class GithubRepository(CodeRepository):
    __pluralname__ = 'github_repositories'

    id =            DB.Column(DB.Integer, DB.ForeignKey('code_repository.id', ondelete='CASCADE'), primary_key=True)
    name =          DB.Column(DB.String, nullable=False)
    repo_id =       DB.Column(DB.Integer, nullable=False, unique=True)
    description =   DB.Column(DB.String, nullable=True)
    project_id =    DB.Column(DB.Integer, DB.ForeignKey('github_project.id',   ondelete='CASCADE'))

    __mapper_args__ = { 'polymorphic_identity': 'github_repository' }

    def __init__(self, project, name, repo_id, repo_url, description):
        self.name = name
        self.repo_id = repo_id
        self.description = description
        self.project = project
        super().__init__(repo_url)

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.GithubProject,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.GithubProject,
            models.CodeClearance,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.GithubProject,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return self.project.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    def __repr__(self):
        return '<GithubRepository[{}]>'.format(self.id)
