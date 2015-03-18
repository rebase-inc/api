
from alveare.common.database import DB

from alveare.models.bid_limit import BidLimit

class TicketSet(DB.Model):
    __pluralname__ = 'ticket_sets'

    id =         DB.Column(DB.Integer, primary_key=True)
    auction_id = DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), nullable=True)
    bid_limits = DB.relationship(BidLimit, backref='ticket_set', cascade='all, delete-orphan', passive_deletes=True)
    nominations = DB.relationship('Nomination', backref='ticket_set', cascade='all, delete-orphan', passive_deletes=True)

    def add_bid_limit(self, bid_limit):
        self.bid_limits.append(bid_limit)

    def __repr__(self):
        return '<Ticketset[id:{}]>'.format(self.id)

