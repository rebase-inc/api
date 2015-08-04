
from rebase.common.database import DB, PermissionMixin
from rebase.models import Nomination

class JobFit(DB.Model, PermissionMixin):
    __pluralname__ = 'job_fits'

    contractor_id = DB.Column(DB.Integer,  primary_key=True)
    ticket_set_id = DB.Column(DB.Integer,  primary_key=True)
    score =                    DB.Column(DB.Integer, nullable=False, default=0)

    ticket_matches = DB.relationship('TicketMatch', backref='job_fit', cascade="all")

    __table_args__ = (
        DB.ForeignKeyConstraint(
            [contractor_id, ticket_set_id],
            [Nomination.contractor_id, Nomination.ticket_set_id],
            ondelete='CASCADE'
        ), {})

    def __init__(self, nomination, ticket_matches):
        if not ticket_matches:
            raise ValueError('JobFit must have at least one instance of a TicketMatch')
        if len(ticket_matches) != len(nomination.ticket_set.bid_limits):
            raise ValueError('JobFit must be initialized with one instance of a TicketMatch for each ticket in the relation auction')
        self.nomination = nomination
        self.ticket_matches = ticket_matches

    def __repr__(self):
        return '<JobFit[contractor({}), auction({})] score={}>'.format(self.contractor_id, self.nomination.auction, self.score)

    @classmethod
    def query_by_user(cls, user):
        return cls.query

    def allowed_to_be_created_by(self, user):
        return True

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    def __repr__(self):
        return '<Ticket[{}] title="{}">'.format(self.id, self.title)
