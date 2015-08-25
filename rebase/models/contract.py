from sqlalchemy import or_, sql
from rebase.common.database import DB, PermissionMixin

class Contract(DB.Model, PermissionMixin):
    __pluralname__ = 'contracts'

    id = DB.Column(DB.Integer, DB.ForeignKey('bid.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, bid):
        self.bid = bid
        for work_offer in bid.work_offers:
            Work(work_offer)

    @classmethod
    def query_by_user(cls, user):
        from rebase.models import Bid, Contractor, User
        query = cls.query
        if user.is_admin():
            return query
        query = query.join(Contract.bid)
        query = query.join(Bid.auction)
        query = query.join(Bid.contractor)
        query = query.join(Contractor.user)

        all_filters = []
        if user.manager_for_organizations:
            all_filters.append(User.id.in_([m.user.id for m in user.manager_roles]))
        all_filters.append(User.id == user.id)
        return query.filter(or_(*all_filters))

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return bool(self.bid.contractor.user == user)

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return (self.bid.auction.organization.id in user.manager_for_organizations) or (self.bid.contractor.user == user)

    def __repr__(self):
        return '<Contract[{}]>'.format(self.id)

