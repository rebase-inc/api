
from alveare.common.database import DB

class Ticket(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String, nullable=False)
    description = DB.Column(DB.String, nullable=False)
    project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id'))

    def __init__(self, project, title, description=''):
        self.project = project
        self.title = title
        self.description = description

    def __repr__(self):
        return '<Ticket[id:{}] title="{}", description="{}">'.format(self.id, self.title, self.description)
