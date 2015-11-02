
from rebase.common.database import DB

from rebase.models.project import Project

class RemoteProject(Project):
    __pluralname__ = 'remote_projects'

    id = DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'remote_project' }

    def __repr__(self):
        return '<RemoteProject[{}] "{}" for "{}">'.format(self.id, self.name, self.organization.name)

