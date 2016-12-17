from rebase.common.database import DB, PermissionMixin
from rebase.common.query import query_from_class_to_user


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

    def __init__(self, auction, contractor, work_offers):
        from rebase.models import WorkOffer
        self.auction = auction
        self.contractor = contractor
        self.work_offers = work_offers

    def as_manager(user):
        import rebase.models as models
        return query_from_class_to_user(Bid, [
            models.Auction,
            models.TicketSet,
            models.BidLimit,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Manager,
        ], user)

    def as_contractor(user):
        import rebase.models as models
        return query_from_class_to_user(Bid, [
            models.Auction,
            models.Nomination,
            models.Contractor,
        ], user)

    def _all(user):
        return Bid.as_contractor(user).union(Bid.as_manager(user))

    @classmethod
    def query_by_user(cls, user):
        if user.is_admin():
            return cls.query
        return cls._all(user)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True
        return Bid.as_contractor(user).first()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return Bid._all(user).filter(Bid.id==self.id).first()

    def __repr__(self):
        return '<Bid[auction({}), contractor({})]>'.format(self.auction_id, self.contractor_id)

