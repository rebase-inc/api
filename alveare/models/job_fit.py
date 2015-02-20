
from alveare.common.database import DB
from alveare.models import Candidate

class JobFit(DB.Model):
    __table_args__ = (DB.ForeignKeyConstraint(  ['contractor_id',           'auction_id'],
                                                [Candidate.contractor_id, Candidate.auction_id], ondelete='CASCADE'), {})

    contractor_id =         DB.Column(DB.Integer,  primary_key=True, nullable=False)
    auction_id =            DB.Column(DB.Integer,  primary_key=True, nullable=False)
    score =                 DB.Column(DB.Integer, nullable=False, default=0)

    ticket_matches =    DB.relationship('TicketMatch', backref='job_fit')

    def __init__(self, candidate, ticket_matches):
        if not ticket_matches:
            raise ValueError('JobFit must have at least one instance of a TicketMatch')
        if len(ticket_matches) != len(candidate.ticket_set.bid_limits):
            raise ValueError('JobFit must be initialized with one instance of a TicketMatch for each ticket in the relation auction')
        self.candidate = candidate
        self.ticket_matches = ticket_matches
        self.score = sum([match.score for match in ticket_matches])//len(ticket_matches) # it's not that simple!

    def __repr__(self):
        return '<JobFit[contractor({}), auction({})] score={}>'.format(self.contractor_id, self.auction_id, self.score)

