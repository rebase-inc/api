from sqlalchemy.orm import validates

import alveare

from alveare.common.database import DB

class WorkOffer(DB.Model):
    __pluralname__ = 'work_offers'

    id =                    DB.Column(DB.Integer, primary_key = True)
    price =                 DB.Column(DB.Integer, nullable=False)
    work_id =               DB.Column(DB.Integer, DB.ForeignKey('work.id',            ondelete='CASCADE'), nullable=True)
    bid_id =                DB.Column(DB.Integer, DB.ForeignKey('bid.id',             ondelete='CASCADE'), nullable=True)
    contractor_id =         DB.Column(DB.Integer, DB.ForeignKey('contractor.id',      ondelete='CASCADE'), nullable=False)
    ticket_snapshot_id =    DB.Column(DB.Integer, DB.ForeignKey('ticket_snapshot.id', ondelete='CASCADE'), nullable=False)

    ticket_snapshot =       DB.relationship('TicketSnapshot', uselist=False)

    def __init__(self, contractor, ticket_snapshot, price):
        # TODO: Get rid of this horrible hack by using composite primary key
        if WorkOffer.query.filter(WorkOffer.contractor == contractor, WorkOffer.ticket_snapshot == ticket_snapshot).all():
            raise ValueError('such a work offer already exists!')
        self.contractor = contractor
        self.ticket_snapshot = ticket_snapshot
        self.price = price

    def __repr__(self):
        return '<WorkOffer[{id}] for snapshot {ticket_snapshot_id} on bid {bid_id} at {price} dollars>'.format(**self.__dict__)

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
