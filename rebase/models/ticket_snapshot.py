from datetime import datetime

from rebase.common.database import DB, PermissionMixin
from rebase.common.query import query_from_class_to_user


class TicketSnapshot(DB.Model, PermissionMixin):
    __pluralname__ = 'ticket_snapshots'

    id =            DB.Column(DB.Integer, primary_key=True)
    title =         DB.Column(DB.String, nullable=False)
    date =          DB.Column(DB.DateTime, nullable=False)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), nullable=True)
    bid_limit =     DB.relationship('BidLimit', uselist=False, backref='ticket_snapshot', cascade='all, delete-orphan', passive_deletes=False)

    def __init__(self, ticket):
        self.date =  datetime.now()
        self.ticket = ticket
        self.title = ticket.title

    @classmethod
    def as_owner(cls, user):
        return cls.as_manager(user)

    @classmethod
    def as_contractor(cls, user):
        return cls.as_contractor_work_offers(user).union(cls.as_contractor_auctions(user))

    @classmethod
    def as_manager(cls, user):
        import rebase.models
        return query_from_class_to_user(TicketSnapshot, [
            rebase.models.ticket.Ticket,
            rebase.models.project.Project,
            rebase.models.organization.Organization,
            rebase.models.manager.Manager,
        ], user)

    @classmethod
    def as_contractor_work_offers(cls, user):
        import rebase.models
        return query_from_class_to_user(TicketSnapshot, [
            rebase.models.work_offer.WorkOffer,
            rebase.models.contractor.Contractor,
        ], user)

    @classmethod
    def as_contractor_auctions(cls, user):
        import rebase.models
        return query_from_class_to_user(TicketSnapshot, [
            rebase.models.bid_limit.BidLimit,
            rebase.models.ticket_set.TicketSet,
            rebase.models.auction.Auction,
            rebase.models.nomination.Nomination,
            rebase.models.contractor.Contractor,
        ], user)

    def allowed_to_be_created_by(self, user):
        return self.ticket.allowed_to_be_created_by(user)

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    @property
    def organization(self):
        return self.ticket.organization

    def __repr__(self):
        return '<TicketSnapshot[id:{}] "{}" date={} ticket_id={}>'.format(self.id, self.title, self.date, self.ticket_id)


