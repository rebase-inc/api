
from alveare.common.database import DB
from alveare.models.ticket import Ticket
from datetime import datetime

class TicketSnapshot(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    date = DB.Column(DB.DateTime, nullable=False)
    bid_limit_id = DB.Column(DB.Integer, DB.ForeignKey('bid_limit.id'))
    ticket_id = DB.Column(DB.Integer, DB.ForeignKey('ticket.id'))
    ticket = DB.relationship(Ticket)

    def __init__(self, ticket):
        self.date =  datetime.now()
        self.ticket = ticket
        self.title = ticket.title
        self.description = ticket.description

    def __repr__(self):
	    return '<TicketSnapshot[id:{}] "{}" date={}>'.format(self.id, self.title, self.date)
