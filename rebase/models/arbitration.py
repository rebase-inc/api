from sqlalchemy.orm import validates

from .mediation import Mediation

from rebase.common.database import DB, PermissionMixin

class Arbitration(DB.Model, PermissionMixin):
    __pluralname__ = 'arbitrations'

    id =            DB.Column(DB.Integer, primary_key=True)
    mediation_id =  DB.Column(DB.Integer, DB.ForeignKey('mediation.id', ondelete='CASCADE'), nullable=False)

    def __init__(self, mediation):
        self.mediation = mediation

    def __repr__(self):
        return '<Arbitration[id:{}] for {}>'.format(self.id, self.mediation)

    @classmethod
    def query_by_user(cls, user):
        from rebase.models import Mediation, Work, WorkOffer, Contractor, Bid, Auction, TicketSet
        from rebase.models import User, BidLimit, TicketSnapshot, Ticket , Organization

        query = cls.query

        if user.is_admin():
            return query

        query_contractor = query.join(cls.mediation)
        query_contractor = query_contractor.join(Mediation.work)
        query_contractor = query_contractor.join(Work.offer)
        query_contractor = query_contractor.join(WorkOffer.contractor)
        query_contractor = query_contractor.join(WorkOffer.contractor)
        query_contractor = query_contractor.join(Contractor.user)
        query_contractor = query_contractor.filter(User.id == user.id)

        if user.manager_for_projects:
            query_manager = query.join(cls.mediation)
            query_manager = query_manager.join(Mediation.work)
            query_manager = query_manager.join(Work.offer)
            query_manager = query_manager.join(WorkOffer.bid)
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
        return user.is_admin()

    def allowed_to_be_modified_by(self, user):
        return user.is_admin()

    def allowed_to_be_deleted_by(self, user):
        return user.is_admin()

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        elif self.mediation.work.offer.contractor.user == user:
            return True
        elif self.mediation.work.offer.bid.auction.organization.id in user.manager_for_projects:
            return True
        else:
            return False

    @validates('mediation')
    def validate_work_offer(self, field, value):
        if not isinstance(value, Mediation):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, Mediation))
        return value


