
from alveare.common.database import DB

from alveare.models.remote_project import RemoteProject

class GithubProject(RemoteProject):
    github_project_id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.remote_project_id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'remote_project' }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<GithubProject[id:{}]>'.format(self.github_project_id)

