from alveare.common.database import DB
from alveare.models.bid_limit import BidLimit

class TicketSet(DB.Model):
    __pluralname__ = 'ticket_sets'

    id =         DB.Column(DB.Integer, primary_key=True)
    auction_id = DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), nullable=True)
    bid_limits = DB.relationship(BidLimit,
        backref=DB.backref('ticket_set', cascade='all, delete-orphan', single_parent=True),
        cascade='all, delete-orphan',
        passive_deletes=True)
    nominations = DB.relationship('Nomination', backref='ticket_set', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, bid_limits):
        self.bid_limits = bid_limits

    @property
    def organization(self):
        return self.bid_limits[0].ticket_snapshot.ticket.organization

    def __repr__(self):
        return '<Ticketset[id:{}]>'.format(self.id)

