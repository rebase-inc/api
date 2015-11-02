
from rebase.common.database import DB

from rebase.models.remote_project import RemoteProject

class InternalProject(RemoteProject):
    __pluralname__ = 'internal_projects'

    id = DB.Column(DB.Integer, DB.ForeignKey('remote_project.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'internal_project' }

    def __repr__(self):
        return '<InternalProject[id:{} "{}"]>'.format(self.id, self.name)
