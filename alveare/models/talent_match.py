
from alveare.common.database import DB

class TalentMatch(DB.Model):

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id',         ondelete='CASCADE'), primary_key=True, nullable=False)
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('ticket_set.auction_id', ondelete='CASCADE'), primary_key=True, nullable=False)
    score =         DB.Column(DB.Integer, nullable=False)

    contractor = DB.relationship('Contractor',  uselist=False)
    ticket_set =    DB.relationship('TicketSet',     uselist=False)

    def __init__(self, contractor, ticket_set, score):
        self.contractor = contractor
        self.ticket_set = ticket_set
        self.score = score

    def __repr__(self):
        return '<TalentMatch[contractor({}), auction({})] score={}>'.format(self.contractor_id, self.auction_id, self.score)

