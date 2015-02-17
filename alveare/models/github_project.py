
from alveare.common.database import DB

from alveare.models.remote_project import RemoteProject

class GithubProject(RemoteProject):
    id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.id'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'remote_project' }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<GithubProject[id:{}]>'.format(self.id)

