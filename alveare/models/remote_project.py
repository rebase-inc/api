
from alveare.common.database import DB

from alveare.models.project import Project

class RemoteProject(Project):
    remote_project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'remote_project' }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<RemoteProject[{}] "{}" for "{}">'.format(self.remote_project_id, self.name, self.organization.name)

