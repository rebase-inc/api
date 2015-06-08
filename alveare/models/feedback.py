from sqlalchemy import or_, sql
from alveare.common.database import DB, PermissionMixin

class Feedback(DB.Model, PermissionMixin):
    __pluralname__ = 'feedbacks'

    id =        DB.Column(DB.Integer, primary_key=True)

    # note these 2 together form a primary key, so bid_id is redundant
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'), nullable=False)
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'), nullable=False)

    comment = DB.relationship('Comment', backref='feedback', lazy='joined', cascade='all, delete-orphan', passive_deletes=True, uselist=False)

    def __init__(self, auction, contractor):
        self.auction = auction
        self.contractor = contractor

    @classmethod
    def query_by_user(cls, user):
        from alveare.models import Contractor, User
        query = cls.query
        if user.is_admin():
            return query
        query = query.join(cls.contractor)
        query = query.join(Contractor.user)

        auctions_approved_for = []
        for contractor in user.contractor_roles.all():
            auctions_approved_for.extend(contractor.auctions_approved_for)

        all_filters = []
        if auctions_approved_for:
            all_filters.append(Feedback.auction.organization_id.in_(user.manager_for_organizations))
        all_filters.append(User.id == user.id)
        return query.filter(or_(*all_filters))

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
        return (self.auction.organization.id in user.manager_for_organizations) or (self.contractor.user == user)

    def __repr__(self):
        return '<Feedback[auction({}), contractor({})] >'.format(self.auction_id, self.contractor_id)
