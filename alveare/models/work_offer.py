
import alveare

from alveare.common.database import DB

class WorkOffer(DB.Model):
    id =      DB.Column(DB.Integer, primary_key=True)
    price =   DB.Column(DB.Integer, nullable=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=True)
    ticket_snapshot_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_snapshot.id', ondelete='CASCADE'), nullable=False)
    ticket_snapshot = DB.relationship('TicketSnapshot', uselist=False)
    bid_id = DB.Column(DB.Integer, DB.ForeignKey('bid.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, bid, ticket_snapshot, price):
        self.bid = bid
        self.ticket_snapshot = ticket_snapshot
        self.price = price

    def __repr__(self):
        return '<WorkOffer for {} {}>'.format(self.price, 'dollars')
