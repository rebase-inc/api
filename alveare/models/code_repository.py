
from alveare.common.database import DB

class CodeRepository(DB.Model):
    __pluralname__ = 'code_repositories'

    id = DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, project):
        self.project = project

    def __repr__(self):
        return '<CodeRepository[id:{}]>'.format(self.id)

