
from alveare.common.database import DB

class Candidate(DB.Model):

    contractor_id =         DB.Column(DB.Integer, DB.ForeignKey('contractor.id',         ondelete='CASCADE'), primary_key=True)
    auction_id =            DB.Column(DB.Integer, DB.ForeignKey('ticket_set.auction_id', ondelete='CASCADE'), primary_key=True)
    approved_auction_id =   DB.Column(DB.Integer, DB.ForeignKey('auction.id'), nullable=True)

    #contractor =    DB.relationship('Contractor',   backref='candidates', uselist=False)
    #contractor =    DB.relationship('Contractor',   uselist=False)
    ticket_set =    DB.relationship('TicketSet',    backref='candidates', uselist=False)
    job_fit =       DB.relationship('JobFit',       backref=DB.backref('candidate', uselist=False), uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, contractor, ticket_set):
        self.contractor = contractor
        self.ticket_set = ticket_set

    def __repr__(self):
        return '<Candidate[contractor({}), auction({})]>'.format(self.contractor_id, self.auction_id)

