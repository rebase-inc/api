from sqlalchemy.orm import validates

from alveare.common.database import DB
from alveare.models.ticket_snapshot import TicketSnapshot

class BidLimit(DB.Model):

    id =        DB.Column(DB.Integer, primary_key=True)
    price =     DB.Column(DB.Integer, nullable=False)
    snapshot =  DB.relationship(TicketSnapshot, uselist=False, cascade='all, delete-orphan')
    auction_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_set.auction_id'), nullable=False)

    def __init__(self, ticket, price):
        self.price = price
        self.snapshot = TicketSnapshot(ticket)

    def __repr__(self):
        return '<BidLimit for auction:{}, price:{} {}>'.format(self.auction_id, self.price, 'dollars')

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        if value < 0:
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, '> 0'))
        return value
