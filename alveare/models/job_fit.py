
from alveare.common.database import DB

class JobFit(DB.Model):
    __table_args__ = (DB.ForeignKeyConstraint(  ['contractor_id',           'auction_id'],
                                                ['candidate.contractor_id',   'candidate.auction_id']), {})

    contractor_id =         DB.Column(DB.Integer,  primary_key=True, nullable=False)
    auction_id =            DB.Column(DB.Integer,  primary_key=True, nullable=False)
    score =                 DB.Column(DB.Integer, nullable=False, default=0)

    ticket_matches =    DB.relationship('TicketMatch', backref='candidate')

    def __init__(self, contractor, ticket_set):
        self.contractor = contractor
        self.ticket_set = ticket_set

    def __repr__(self):
        return '<JobFit[contractor({}), auction({})] score={}>'.format(self.contractor_id, self.auction_id, self.score)

