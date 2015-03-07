
from alveare.common.database import DB
from alveare.models.ticket import Ticket

class RemoteTicket(Ticket):
    id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), primary_key=True)

    __mapper_args__ = { 'polymorphic_identity': 'remote_ticket' }

    def __init__(self, *args, **kwargs):
        raise NotImplementedError()

    def __repr__(self):
        return '<RemoteTicket[id:{}]>'.format(self.id)

