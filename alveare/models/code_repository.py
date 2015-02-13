
from alveare.common.database import DB

class CodeRepository(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, project):
        self.project = project

    def __repr__(self):
        return '<CodeRepository[id:{}]>'.format(self.id)

