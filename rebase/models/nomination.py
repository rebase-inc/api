from sqlalchemy import or_, sql

from rebase.common.database import DB, PermissionMixin
from rebase.common.email import Email, send

class Nomination(DB.Model, PermissionMixin):
    __pluralname__ = 'nominations'

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    ticket_set_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_set.id', ondelete='CASCADE'), primary_key=True)
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), nullable=True)
    hide =          DB.Column(DB.Boolean, nullable=False, default=False)

    job_fit = DB.relationship('JobFit', backref=DB.backref('nomination', uselist=False), uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    @property
    def organization(self):
        return self.ticket_set.bid_limits[0].ticket_snapshot.ticket.organization

    @property
    def auction(self):
        return self._auction

    @auction.setter
    def auction(self, value):
        from rebase.models import CodeClearance
        project = value.ticket_set.bid_limits[0].ticket_snapshot.ticket.project
        if not CodeClearance.query.filter(CodeClearance.contractor_id == self.contractor_id).filter(CodeClearance.project_id == project.id).first():
            CodeClearance(project, self.contractor)
        self._auction = value
        send_email(self)

    def __init__(self, contractor, ticket_set, auction=None):
        from rebase.models import Contractor, TicketSet, TicketMatch, JobFit
        if not isinstance(contractor, Contractor):
            raise ValueError('contractor must be of Contractor type!')
        if not isinstance(ticket_set, TicketSet):
            raise ValueError('ticket_set must be of TicketSet type!')
        self.contractor = contractor
        self.ticket_set = ticket_set
        if auction:
            self.auction = auction
        ticket_matches = []
        for bid_limit in ticket_set.bid_limits:
            skill_requirement = bid_limit.ticket_snapshot.ticket.skill_requirement
            ticket_match = TicketMatch.query.get((skill_requirement.id, contractor.skill_set.id))
            ticket_match = ticket_match or TicketMatch(contractor.skill_set, skill_requirement)
            ticket_matches.append(ticket_match)
        job_fits = JobFit(self, ticket_matches)

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.Contractor
        ]
        cls.as_manager_path = [
            models.TicketSet,
            models.BidLimit,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager
        ]
        cls.as_owner_path = [
            models.TicketSet,
            models.BidLimit,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Owner
        ]

    def allowed_to_be_created_by(self, user):
        return self.ticket_set.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    def __repr__(self):
        return '<Nomination[contractor({}), ticket_set({})]>'.format(self.contractor_id, self.ticket_set_id)


def send_email(nomination):
    ticket = nomination.ticket_set.bid_limits[0].ticket_snapshot.ticket
    contractor = nomination.contractor.user
    contractor_text = 'Waiting for your bid on ticket:\n"{title}"'.format(title=ticket.title)
    contractor_email = Email(
        'do_not_reply@rebaseapp.com',
        [ contractor.email ],
        'Rebase Auction: bid for ticket "{}"'.format(ticket.title),
        contractor_text,
        contractor_text,
    )
    send([ contractor_email ])


