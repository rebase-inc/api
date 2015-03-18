
from alveare.common.database import DB

class Candidate(DB.Model):
    __pluralname__ = 'candidates'

    contractor_id =           DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    ticket_set_id =           DB.Column(DB.Integer, DB.ForeignKey('ticket_set.id', ondelete='CASCADE'), primary_key=True)
    approved_for_auction_id = DB.Column(DB.Integer, DB.ForeignKey('auction.id'), nullable=True)

    job_fit = DB.relationship('JobFit', backref=DB.backref('candidate', uselist=False), uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, contractor, ticket_set):
        from alveare.models import Contractor, TicketSet
        if not isinstance(contractor, Contractor):
            raise ValueError('contractor must be of Contractor type!')
        if not isinstance(ticket_set, TicketSet):
            raise ValueError('ticket_set must be of TicketSet type!')
        self.contractor = contractor
        self.ticket_set = ticket_set

    def __repr__(self):
        return '<Candidate[contractor({}), ticket_set({})]>'.format(self.contractor_id, self.ticket_set_id)

