
from alveare.common.database import DB

class Ticket(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String, nullable=False)
    description = DB.Column(DB.String, nullable=False)
    project_id = DB.Column(DB.Integer, DB.ForeignKey('project.id'))
    type = DB.Column(DB.String)
    snapshots = DB.relationship('TicketSnapshot', backref='ticket', cascade='all, delete-orphan', passive_deletes=True)
    comments = DB.relationship('Comment', backref='ticket', cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = {
        'polymorphic_identity': 'ticket',
        'polymorphic_on': type
    }

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def __repr__(self):
        return '<Ticket[id:{}] title="{}", description="{}">'.format(self.id, self.title, self.description)
