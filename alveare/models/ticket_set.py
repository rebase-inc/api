
from alveare.common.database import DB

from alveare.models.bid_limit import BidLimit

class TicketSet(DB.Model):
    
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    bid_limits =    DB.relationship(BidLimit, backref='ticket_set', cascade='all, delete-orphan', passive_deletes=True)

    def add_bid_limit(self, bid_limit):
        self.bid_limits.append(bid_limit)

    def __repr__(self):
        return '<Ticketset[id:{}]>'.format(self.auction_id)

