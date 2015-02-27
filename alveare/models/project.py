
from alveare.common.database import DB

class Project(DB.Model):
    id =                DB.Column(DB.Integer, primary_key=True)
    name =              DB.Column(DB.String, nullable=False)
    organization_id =   DB.Column(DB.Integer, DB.ForeignKey('organization.id'))
    type =              DB.Column(DB.String)

    code_repository =   DB.relationship('CodeRepository', uselist=False, backref='project', cascade="all, delete-orphan", passive_deletes=True)
    tickets =           DB.relationship('Ticket', backref='project', cascade="all, delete-orphan", passive_deletes=True)
    clearances =        DB.relationship('CodeClearance', backref='project', cascade="all, delete-orphan", passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'project',
        'polymorphic_on': type
    }

    def __init__(self, organization, name):
        self.organization = organization
        self.name = name

    def __repr__(self):
        return '<Project[id:{}] for "{}" >'.format(self.id, self.organization)

