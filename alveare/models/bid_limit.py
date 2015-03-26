from sqlalchemy.orm import validates

from alveare.common.database import DB
from alveare.models.ticket_snapshot import TicketSnapshot

class BidLimit(DB.Model):
    __pluralname__ = 'bid_limits'

    id =            DB.Column(DB.Integer, primary_key=True)
    price =         DB.Column(DB.Integer, nullable=False)
    ticket_set_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_set.id', ondelete='CASCADE'), nullable=True)
    ticket_snapshot_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_snapshot.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, ticket_snapshot, price):
        if not isinstance(ticket_snapshot, TicketSnapshot):
            raise ValueError('ticket_snapshot parameter must be of type TicketSnapshot')
        self.ticket_snapshot = ticket_snapshot
        self.price = price

    @property
    def organization(self):
        return self.ticket_snapshot.ticket.organization

    def __repr__(self):
        return '<BidLimit for snapshot: {} on ticket_set:{}, price:{} {}>'.format(self.ticket_snapshot_id, self.ticket_set_id, self.price, 'dollars')

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        if value < 0:
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, '> 0'))
        return value
