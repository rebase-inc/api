from sqlalchemy.orm import validates

from rebase.common.database import DB, PermissionMixin
from rebase.common.exceptions import AlreadyBid

class WorkOffer(DB.Model, PermissionMixin):
    __pluralname__ = 'work_offers'

    id =                    DB.Column(DB.Integer, primary_key = True)
    price =                 DB.Column(DB.Integer, nullable=False)
    work_id =               DB.Column(DB.Integer, DB.ForeignKey('work.id',            ondelete='CASCADE'), nullable=True)
    bid_id =                DB.Column(DB.Integer, DB.ForeignKey('bid.id',             ondelete='CASCADE'), nullable=True)
    contractor_id =         DB.Column(DB.Integer, DB.ForeignKey('contractor.id',      ondelete='CASCADE'), nullable=False)
    ticket_snapshot_id =    DB.Column(DB.Integer, DB.ForeignKey('ticket_snapshot.id', ondelete='CASCADE'), nullable=False)

    ticket_snapshot =       DB.relationship('TicketSnapshot', uselist=False)

    def __init__(self, contractor, ticket_snapshot, price):
        # TODO: Get rid of this horrible hack by using composite primary key
        if WorkOffer.query.filter(WorkOffer.contractor == contractor, WorkOffer.ticket_snapshot == ticket_snapshot).all():
            raise AlreadyBid(contractor, ticket_snapshot)
        self.contractor = contractor
        self.ticket_snapshot = ticket_snapshot
        self.price = price

    @classmethod
    def query_by_user(cls, user):
        from rebase.models import Contractor, Bid, Auction, TicketSet, User
        from rebase.models import BidLimit, TicketSnapshot, Ticket , Organization
        query = cls.query

        if user.is_admin(): return query

        query_contractor = query.join(cls.contractor)
        query_contractor = query_contractor.join(Contractor.user)
        query_contractor = query_contractor.filter(User.id == user.id)

        if user.manager_for_projects:
            query_manager = query.join(cls.bid)
            query_manager = query_manager.join(Bid.auction)
            query_manager = query_manager.join(Auction.ticket_set)
            query_manager = query_manager.join(TicketSet.bid_limits)
            query_manager = query_manager.join(BidLimit.ticket_snapshot)
            query_manager = query_manager.join(TicketSnapshot.ticket)
            query_manager = query_manager.join(Ticket.organization)
            query_manager = query_manager.filter(Organization.id.in_(user.manager_for_projects))
            query_contractor = query_contractor.union(query_manager)

        return query_contractor

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return bool(self.contractor.user == user)

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return (self.bid and self.bid.auction.organization.id in user.manager_for_projects) or (self.contractor.user == user)

    def __repr__(self):
        return 'Work Offer: {}'.format(self.__dict__)
        return '<WorkOffer[{}] for snapshot {ticket_snapshot_id} on bid {bid_id} at {price} dollars>'.format(self.id, **self.__dict__)

    @validates('price')
    def validate_price(self, field, value):
        if not isinstance(value, int):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, int))
        return value
