
from alveare.common.database import DB
from alveare.models.ticket import Ticket
from datetime import datetime

class TicketSnapshot(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    date =          DB.Column(DB.DateTime, nullable=False)
    bid_limit_id =  DB.Column(DB.Integer, DB.ForeignKey('bid_limit.id'), nullable=False)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id'), nullable=False)
    ticket =        DB.relationship(Ticket, uselist=False)

    def __init__(self, ticket):
        self.date =  datetime.now()
        self.ticket = ticket

    def __repr__(self):
	    return '<TicketSnapshot[id:{}] date: {}>'.format(self.id, self.date)
