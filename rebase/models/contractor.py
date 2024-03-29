from random import randint

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import aliased, reconstructor

from rebase.models.role import Role
from rebase.models.user import User
from rebase.common.database import DB
from rebase.common.query import query_from_class_to_user, query_by_user_or_id
import rebase.models

class Contractor(Role):
    __pluralname__ = 'contractors'

    id =            DB.Column(DB.Integer, DB.ForeignKey('role.id', ondelete='CASCADE'), primary_key=True)
    busyness =      DB.Column(DB.Integer, nullable=False, default=1)
    rate =          DB.Column(DB.Integer, nullable=False, default=0)
    rating =        DB.Column(DB.Float, nullable=False) # this will probably end up being a composite of the users reviews, but I needed something temporarily

    clearances =          DB.relationship('CodeClearance',     backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    skill_set =           DB.relationship('SkillSet',          uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    remote_work_history = DB.relationship('RemoteWorkHistory', uselist=False, backref='contractor', cascade='all, delete-orphan', passive_deletes=True)
    auction_nominations = DB.relationship('Nomination',        backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)
    bank_account =        DB.relationship('BankAccount',       backref='contractor', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    work_offers =         DB.relationship('WorkOffer',         backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)
    bids =                DB.relationship('Bid',               backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)
    feedbacks =           DB.relationship('Feedback',          backref=DB.backref('contractor', uselist=False), cascade='all, delete-orphan', passive_deletes=True)

    __mapper_args__ = { 'polymorphic_identity': 'contractor' }

    def __init__(self, user):
        self.user = user
        self.busyness = 1
        self.rating = 0
        from rebase.models.skill_set import SkillSet
        SkillSet(self)

    @reconstructor
    def init(self):
        from rebase.models.review import Review
        old_filter = Review.filter_based_on_current_role
        Review.filter_based_on_current_role = False
        reviews = Review.as_contractor(self.user).all()
        Review.filter_based_on_current_role = old_filter
        if reviews:
            _sum = 0.0
            for review in reviews:
                _sum += review.rating
            self.rating = _sum/len(reviews)
        else:
            self.rating = 0.0

    @hybrid_property
    def auctions_approved_for(self):
        auctions_approved_for = []
        for nomination in self.auction_nominations:
            approved = nomination.auction
            if approved:
                auctions_approved_for.append(approved.id)
        return auctions_approved_for

    @classmethod
    def as_manager_get_cleared_contractors(cls, current_user):
        query = cls.query\
            .join(rebase.models.code_clearance.CodeClearance)\
            .join(rebase.models.project.Project)\
            .join(rebase.models.manager.Manager)\
            .filter(rebase.models.manager.Manager.user==current_user)
        return query

    nominated_path = None

    @classmethod
    def as_manager_get_nominated_contractors(cls, current_user):
        query = cls.query
        if not cls.nominated_path:
            cls.nominated_path = [
                rebase.models.nomination.Nomination,
                rebase.models.ticket_set.TicketSet,
                rebase.models.bid_limit.BidLimit,
                rebase.models.ticket_snapshot.TicketSnapshot,
                rebase.models.ticket.Ticket,
                rebase.models.project.Project,
                rebase.models.manager.Manager,
            ]
        for klass in cls.nominated_path:
            query = query.join(klass)
        query = query.filter(rebase.models.manager.Manager.user==current_user)
        return query

    @classmethod
    def as_contractor_get_cleared_contractors(cls, user):
        import rebase.models
        ct = aliased(rebase.models.Contractor)
        return DB.session.query(ct)\
            .select_from(Contractor)\
            .filter(Contractor.user==user)\
            .join(rebase.models.CodeClearance)\
            .join(rebase.models.Project)\
            .join(rebase.models.CodeClearance, aliased=True)\
            .join(ct)

    def filter_by_id(self, query):
        return query.filter(Contractor.id==self.id)

    @classmethod
    def _all(cls, user):
        return cls.as_manager_get_cleared_contractors(user)\
            .union(cls.as_manager_get_nominated_contractors(user))\
            .union(cls.as_contractor_get_cleared_contractors(user))

    @classmethod
    def get_all(cls, user, comment=None):
        return query_by_user_or_id(
            cls,
            cls._all,
            cls.filter_by_id,
            user, comment
        )

    def allowed_to_be_created_by(self, user):
        return user.is_admin() or self.user == user

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return True

    @classmethod
    def query_by_user(cls, user):
        return cls.get_all(user)

    def __repr__(self):
        return '<Contractor[id:{} "{}"] busyness="{}">'.format(
            self.id,
            self.user.name,
            self.busyness
        )
