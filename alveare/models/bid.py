from alveare.common.database import DB, PermissionMixin

from sqlalchemy import or_, sql

class Bid(DB.Model, PermissionMixin):
    __pluralname__ = 'bids'

    id =        DB.Column(DB.Integer, primary_key=True)

    # note these 2 together form a primary key, so bid_id is redundant
    auction_id =    DB.Column(DB.Integer, DB.ForeignKey('auction.id', ondelete='CASCADE'),      nullable=False)
    contractor_id = DB.Column(DB.Integer, DB.ForeignKey('contractor.id', ondelete='CASCADE'),   nullable=False)

    work_offers =   DB.relationship('WorkOffer',
            backref=DB.backref('bid', cascade='all, delete-orphan', single_parent=True),
            lazy='dynamic')

    contract = DB.relationship('Contract', backref='bid', cascade='all, delete-orphan', uselist=False)

    def __init__(self, auction, contractor):
        from alveare.models import WorkOffer
        self.auction = auction
        self.contractor = contractor
        self.work_offers = WorkOffer.query.filter(WorkOffer.contractor == contractor,
            WorkOffer.ticket_snapshot_id.in_([bl.ticket_snapshot.id for bl in auction.ticket_set.bid_limits]))

    @classmethod
    def query_by_user(cls, user):
        from alveare.models import Contractor, User
        query = cls.query
        if user.is_admin():
            return query
        query = query.join(cls.contractor)
        query = query.join(Contractor.user)

        all_filters = []
        if user.manager_for_organizations:
            all_filters.append(User.id.in_([m.user.id for m in user.manager_roles]))
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
        return '<Bid[auction({}), contractor({})]>'.format(self.auction_id, self.contractor_id)

