
from alveare.common.database import DB
from alveare.models.ticket import Ticket

class InternalTicket(Ticket):
    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'internal_ticket' }

    def __init__(self, project, title, description=''):
        self.project = project
        self.title = title
        self.description = description

    def __repr__(self):
        return '<InternalTicket[id:{}]>'.format(self.id)

