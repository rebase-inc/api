from rebase.common.database import DB
from rebase.models.code_repository import CodeRepository

class WorkRepo(CodeRepository):
    __pluralname__ = 'rebase_repos'

    code_repository_id =    DB.Column(DB.Integer, DB.ForeignKey('code_repository.id',   ondelete='CASCADE'),    primary_key=True)
    project_id =            DB.Column(DB.Integer, DB.ForeignKey('project.id',           ondelete='CASCADE'),    primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'rebase_repo' }

    def __init__(self, project):
        self.project = project
        super().__init__('/'.join([self.project.organization.name, self.project.name]))

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.Project,
            models.CodeClearance,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return self.project.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.project.allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<WorkRepo[id:{}]>'.format(self.id)
