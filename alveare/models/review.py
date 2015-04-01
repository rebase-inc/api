from sqlalchemy.orm import validates

from alveare.common.database import DB, PermissionMixin

class Review(DB.Model, PermissionMixin):
    __pluralname__ = 'reviews'

    id =      DB.Column(DB.Integer, primary_key=True)
    rating =  DB.Column(DB.Integer, nullable=False)
    work_id = DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)

    comments = DB.relationship('Comment', lazy='dynamic', backref='review', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work, rating):
        if not isinstance(rating, int):
            raise ValueError('{} field on {} must be {}'.format('rating', self.__tablename__, int))
        if rating < 1 or rating > 5:
            raise ValueError('{} field on {} must be {}'.format('rating', self.__tablename__, 'from 1 to 5'))
        if work.review:
            raise ValueError('Work is already reviewed!')
        self.work = work
        self.rating = rating

    @classmethod
    def query_by_user(cls, user):
        from alveare.models import Work, WorkOffer, Contractor, Bid, Auction, TicketSet, User
        from alveare.models import BidLimit, TicketSnapshot, Ticket , Organization

        query = cls.query

        if user.is_admin():
            return query

        query_contractor = query.join(cls.work)
        query_contractor = query_contractor.join(Work.offer)
        query_contractor = query_contractor.join(WorkOffer.contractor)
        query_contractor = query_contractor.join(Contractor.user)
        query_contractor = query_contractor.filter(User.id == user.id)

        if user.manager_for_organizations:
            query_manager = query.join(cls.work)
            query_manager = query_manager.join(Work.offer)
            query_manager = query_manager.join(WorkOffer.bid)
            query_manager = query_manager.join(Bid.auction)
            query_manager = query_manager.join(Auction.ticket_set)
            query_manager = query_manager.join(TicketSet.bid_limits)
            query_manager = query_manager.join(BidLimit.ticket_snapshot)
            query_manager = query_manager.join(TicketSnapshot.ticket)
            query_manager = query_manager.join(Ticket.organization)
            query_manager = query_manager.filter(Organization.id.in_(user.manager_for_organizations))
            query_contractor = query_contractor.union(query_manager)

        return query_contractor

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return self.work.offer.contractor.user == user

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        elif self.work.offer.contractor.user == user:
            return True
        elif self.work.offer.bid.auction.organization.id in user.manager_for_organizations:
            return True
        else:
            return False

    def __repr__(self):
        return '<Review[{}] rating={}>'.format(self.id, self.rating)
