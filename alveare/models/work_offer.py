from sqlalchemy.orm import validates

import alveare

from alveare.common.database import DB

class WorkOffer(DB.Model):

    __table_args__ = (
        DB.ForeignKeyConstraint(
            ['auction_id', 'contractor_id'],
            ['bid.auction_id', 'bid.contractor_id']),
    )

    price =                 DB.Column(DB.Integer, nullable=False)
    work_id =               DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=True)
    auction_id =            DB.Column(DB.Integer, DB.ForeignKey('auction.id'),      primary_key=True, nullable=False)
    contractor_id =         DB.Column(DB.Integer, DB.ForeignKey('contractor.id'),   primary_key=True, nullable=False)
    ticket_snapshot_id =    DB.Column(DB.Integer, DB.ForeignKey('ticket_snapshot.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    ticket_snapshot =       DB.relationship('TicketSnapshot', uselist=False)

    def __init__(self, bid, ticket_snapshot, price):
        self.bid = bid
        self.ticket_snapshot = ticket_snapshot
        self.price = price

    def __repr__(self):
        return '<WorkOffer[({},{},{})] for {} {}>'.format(self.auction_id,
                                                          self.contractor_id,
                                                          self.ticket_snapshot_id,
                                                          self.price,
                                                          'dollars')
    
    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
