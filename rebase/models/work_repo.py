from os.path import join

from flask.ext.login import current_app
from sqlalchemy.orm import reconstructor

from rebase.common.database import DB
from rebase.models.code_repository import CodeRepository


chars = {
    ord(' '): '_',
    ord('\''): None
}


def normalize(s):
    return s.lower().translate(chars)


class WorkRepo(CodeRepository):
    __pluralname__ = 'rebase_repos'

    code_repository_id =    DB.Column(DB.Integer, DB.ForeignKey('code_repository.id',   ondelete='CASCADE'),    primary_key=True)
    project_id =            DB.Column(DB.Integer, DB.ForeignKey('project.id',           ondelete='CASCADE'),    primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'rebase_repo' }

    def __init__(self, project):
        self.project = project
        super().__init__('')

    @reconstructor
    def init(self):
        self.repo_path = join(
            normalize(self.project.organization.name),
            normalize(self.project.name)
        )
        self.full_repo_path = join(
            current_app.config['WORK_REPOS_ROOT'], 
            self.repo_path
        )
        self.url = current_app.config['GIT_SERVER_URL_PREFIX']+self.repo_path
        self.clone = 'git clone {}'.format(self.url)

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
