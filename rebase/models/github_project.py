
from rebase.common.database import DB
from rebase.models.remote_project import RemoteProject

class GithubProject(RemoteProject):
    __pluralname__ = 'github_projects'

    id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.id', ondelete='CASCADE'), primary_key=True)

    remote_repo = DB.relationship('GithubRepository', backref='project', cascade="all, delete-orphan", passive_deletes=False, uselist=False)
    
    __mapper_args__ = { 'polymorphic_identity': 'github_project' }

    def __init__(self, organization, name, repo_id, repo_url, repo_description):
        from rebase.models.github_repository import GithubRepository
        super().__init__(organization, name)
        GithubRepository(self, name, repo_id, repo_url, repo_description)

    def __repr__(self):
        return '<GithubProject[id:{} "{}"]>'.format(self.id, self.name)
