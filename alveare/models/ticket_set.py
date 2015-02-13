
from alveare.common.database import DB

from alveare.models.bid_limit import BidLimit

class TicketSet(DB.Model):

    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id'), primary_key=True)
    bid_limits =    DB.relationship(BidLimit, backref='ticket_set', cascade='all, delete-orphan')

    def add(self, ticket, price):
        self.bid_limits.append(BidLimit(ticket, price))

    def __repr__(self):
        return '<Ticketset[id:{}]>'.format(self.auction_id)

