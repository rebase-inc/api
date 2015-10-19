
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

    def __repr__(self):
        return '<GithubRepository[{}]>'.format(self.id)
