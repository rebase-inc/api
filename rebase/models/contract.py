from sqlalchemy import or_, sql

from rebase.common.database import DB, PermissionMixin


class Contract(DB.Model, PermissionMixin):
    __pluralname__ = 'contracts'

    id = DB.Column(DB.Integer, DB.ForeignKey('bid.id', ondelete='CASCADE'), primary_key=True)

    def __init__(self, bid):
        from rebase.models import Work
        self.bid = bid
        for work_offer in bid.work_offers:
            Work(work_offer)

    def allowed_to_be_created_by(self, user):
        if user.is_admin():
            return True

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return self.role_to_query_fn(user)(user).filter(Contract.id==self.id).first()

    def __repr__(self):
        return '<Contract[{}]>'.format(self.id)

    @classmethod
    def setup_queries(cls, models):
        Contract.as_contractor_path = [
                models.Bid,
                models.contractor.Contractor,
        ]

        Contract.as_manager_path = [
                models.Bid,
                models.Auction,
                models.TicketSet,
                models.BidLimit,
                models.TicketSnapshot,
                models.Ticket,
                models.Project,
                models.Organization,
                models.Manager,
        ]
