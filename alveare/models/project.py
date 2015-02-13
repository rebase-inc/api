
from alveare.common.database import DB

class Project(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String, nullable=False)
    organization_id = DB.Column(DB.Integer, DB.ForeignKey('organization.id'))
    code_repository = DB.relationship('CodeRepository', uselist=False, backref='project', cascade="all, delete-orphan", passive_deletes=True)
    tickets = DB.relationship('Ticket', backref='project', cascade="all, delete-orphan", passive_deletes=True)

    def __init__(self, name, organization):
        self.name = name
        self.organization = organization

    def __repr__(self):
        return '<Project[id:{}] for "{}" >'.format(self.id, self.organization)

