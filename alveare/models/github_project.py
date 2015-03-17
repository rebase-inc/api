
from alveare.common.database import DB

from alveare.models.remote_project import RemoteProject

class GithubProject(RemoteProject):
    __pluralname__ = 'github_projects'

    id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'github_project' }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<GithubProject[id:{}]>'.format(self.id)

