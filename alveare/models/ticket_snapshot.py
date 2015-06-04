from datetime import datetime

from alveare.common.database import DB, PermissionMixin, query_by_user_or_id

class TicketSnapshot(DB.Model, PermissionMixin):
    __pluralname__ = 'ticket_snapshots'

    id =            DB.Column(DB.Integer, primary_key=True)
    title =         DB.Column(DB.String, nullable=False)
    description =   DB.Column(DB.String, nullable=False)
    date =          DB.Column(DB.DateTime, nullable=False)
    ticket_id =     DB.Column(DB.Integer, DB.ForeignKey('ticket.id', ondelete='CASCADE'), nullable=True)
    bid_limit =     DB.relationship('BidLimit', uselist=False, backref='ticket_snapshot', cascade='all, delete-orphan', passive_deletes=False)

    def __init__(self, ticket):
        self.date =  datetime.now()
        self.ticket = ticket
        self.title = ticket.title
        self.description = ticket.description

    @classmethod
    def query_by_user(cls, user):
        return query_by_user_or_id(cls, cls.get_all, user)

    @classmethod
    def get_all(cls, user, id=None):
        return cls.as_manager(user, id)\
            .union(cls.as_contractor_work_offers(user, id))\
            .union(cls.as_contractor_auctions(user, id))

    @classmethod
    def as_manager(cls, user, id=None):
        import alveare.models.ticket
        query = cls.query
        if id:
            query = query.filter(cls.id==id)
        return query\
            .join(alveare.models.ticket.Ticket)\
            .join(alveare.models.project.Project)\
            .join(alveare.models.organization.Organization)\
            .join(alveare.models.manager.Manager)\
            .filter(alveare.models.manager.Manager.user==user)

    @classmethod
    def as_contractor_work_offers(cls, user, id=None):
        import alveare.models.work_offer
        query = cls.query
        if id:
            query = query.filter(cls.id==id)
        return query\
            .join(alveare.models.work_offer.WorkOffer)\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user==user)

    @classmethod
    def as_contractor_auctions(cls, user, id=None):
        import alveare.models.bid_limit
        query = cls.query
        if id:
            query = query.filter(cls.id==id)
        return query\
            .join(alveare.models.bid_limit.BidLimit)\
            .join(alveare.models.ticket_set.TicketSet)\
            .join(alveare.models.auction.Auction)\
            .join(alveare.models.nomination.Nomination)\
            .join(alveare.models.contractor.Contractor)\
            .filter(alveare.models.contractor.Contractor.user==user)

    def allowed_to_be_created_by(self, user):
        return user.admin or self.as_manager(user, self.id).all()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.admin:
            return True
        return self.get_all(user, self.id).all()

    @property
    def organization(self):
        return self.ticket.organization

    def __repr__(self):
        return '<TicketSnapshot[id:{}] "{}" date={} ticket_id={}>'.format(self.id, self.title, self.date, self.ticket_id)
