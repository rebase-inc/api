
from alveare.common.database import DB
from datetime import datetime

class TicketSnapshot(DB.Model):

    id =            DB.Column(DB.Integer, primary_key=True)
    title =         DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=False)
    date =          DB.Column(DB.DateTime, nullable=False)
    bid_limit_id =  DB.Column(DB.Integer, DB.ForeignKey('bid_limit.id', ondelete='CASCADE'), nullable=False)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id'), nullable=False)

    def __init__(self, ticket):
        self.date =  datetime.now()
        self.ticket = ticket
        self.title = ticket.title
        self.description = ticket.description

    def __repr__(self):
        return '<TicketSnapshot[id:{}] "{}" date={} ticket_id={}>'.format(self.id, self.title, self.date, self.ticket_id)
