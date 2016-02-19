
from rebase.common.database import DB, PermissionMixin
from rebase.models.bid_limit import BidLimit
from rebase.common.query import query_from_class_to_user


class TicketSet(DB.Model, PermissionMixin):
    __pluralname__ = 'ticket_sets'

    id =         DB.Column(DB.Integer, primary_key=True)
    auction_id = DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), nullable=True)
    bid_limits = DB.relationship(
        BidLimit,
        backref=DB.backref('ticket_set', cascade='all, delete-orphan', single_parent=True),
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    nominations = DB.relationship('Nomination', backref='ticket_set', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, bid_limits):
        self.bid_limits = bid_limits

    @property
    def organization(self):
        return self.bid_limits[0].ticket_snapshot.ticket.organization


    @classmethod
    def as_owner(cls, user):
        return cls.as_manager(user)

    @classmethod
    def as_manager(cls, user):
        import rebase.models
        return query_from_class_to_user(TicketSet, [
            rebase.models.bid_limit.BidLimit,
            rebase.models.ticket_snapshot.TicketSnapshot,
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    @classmethod
    def as_contractor(cls, user):
        import rebase.models
        return query_from_class_to_user(TicketSet, [
            rebase.models.nomination.Nomination,
            rebase.models.contractor.Contractor,
        ], user)


    def allowed_to_be_created_by(self, user):
        return self.bid_limits[0].allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.bid_limits[0].allowed_to_be_viewed_by(user)

    def __repr__(self):
        return '<Ticketset[id:{}]>'.format(self.id)


