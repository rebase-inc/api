from datetime import datetime

from alveare.common.database import DB

class TicketSnapshot(DB.Model):
    __pluralname__ = 'ticket_snapshots'

    id =            DB.Column(DB.Integer, primary_key=True)
    title =         DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=False)
    date =          DB.Column(DB.DateTime, nullable=False)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), nullable=True)
    bid_limit =     DB.relationship('BidLimit', uselist=False, backref='ticket_snapshot', cascade='all, delete-orphan', passive_deletes=False)

    def __init__(self, ticket):
        self.date =  datetime.now()
        self.ticket = ticket
        self.title = ticket.title
        self.description = ticket.description

    @property
    def organization(self):
        return self.ticket.organization

    def __repr__(self):
        return '<TicketSnapshot[id:{}] "{}" date={} ticket_id={}>'.format(self.id, self.title, self.date, self.ticket_id)
