
from alveare.common.database import DB

from alveare.models.project import Project

class RemoteProject(Project):
    id = DB.Column(DB.Integer, DB.ForeignKey('project.id'), primary_key=True)

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<RemoteProject[id:{}]>'.format(self.id)

