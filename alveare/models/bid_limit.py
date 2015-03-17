from sqlalchemy.orm import validates

from alveare.common.database import DB
from alveare.models.ticket_snapshot import TicketSnapshot

class BidLimit(DB.Model):
    __pluralname__ = 'bid_limits'

    id =            DB.Column(DB.Integer, primary_key=True)
    price =         DB.Column(DB.Integer, nullable=False)
    ticket_set_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_set.id', ondelete='CASCADE'), nullable=False)

    ticket_snapshot = DB.relationship(TicketSnapshot, uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, ticket_snapshot, price):
        self.price = price
        self.ticket_snapshot = ticket_snapshot

    def __repr__(self):
        return '<BidLimit for ticket_set:{}, price:{} {}>'.format(self.ticket_set_id, self.price, 'dollars')

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        if value < 0:
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, '> 0'))
        return value
