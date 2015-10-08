from sqlalchemy import or_, sql
from rebase.common.database import DB, PermissionMixin

class Nomination(DB.Model, PermissionMixin):
    __pluralname__ = 'nominations'

    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), primary_key=True)
    ticket_set_id = DB.Column(DB.Integer, DB.ForeignKey('ticket_set.id', ondelete='CASCADE'), primary_key=True)
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), nullable=True)

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

    def __init__(self, contractor, ticket_set, auction=None):
        from rebase.models import Contractor, TicketSet
        if not isinstance(contractor, Contractor):
            raise ValueError('contractor must be of Contractor type!')
        if not isinstance(ticket_set, TicketSet):
            raise ValueError('ticket_set must be of TicketSet type!')
        self.contractor = contractor
        self.ticket_set = ticket_set
        if auction:
            self.auction = auction

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        organization_id = self.ticket_set.bid_limits[0].ticket_snapshot.ticket.organization.id
        return bool(organization_id in user.manager_for_projects)

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        return self.allowed_to_be_created_by(user)

    @classmethod
    def query_by_user(cls, user):
        from rebase.models import TicketSet, BidLimit, TicketSnapshot, Ticket, Project, Organization
        query = cls.query
        if user.is_admin():
            return query
        elif user.manager_for_projects:
            query = query.join(cls.ticket_set)
            query = query.join(TicketSet.bid_limits)
            query = query.join(BidLimit.ticket_snapshot)
            query = query.join(TicketSnapshot.ticket)
            query = query.join(Ticket.project)
            query = query.join(Project.organization)
            query = query.filter(Organization.id.in_(user.manager_for_projects))
            return query
        else:
            return query.filter(sql.false())

    def __repr__(self):
        return '<Nomination[contractor({}), ticket_set({})]>'.format(self.contractor_id, self.ticket_set_id)

