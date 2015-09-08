from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from .work_offer import WorkOffer
from .mediation import Mediation
from rebase.common.database import DB, PermissionMixin
from rebase.common.state import StateMachine

class Work(DB.Model, PermissionMixin):
    __pluralname__ = 'work'

    id =    DB.Column(DB.Integer, primary_key=True)
    state = DB.Column(DB.String, nullable=False, default='in_progress')

    debit =             DB.relationship('Debit',     backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    credit =            DB.relationship('Credit',    backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    offer =             DB.relationship('WorkOffer', backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    review =            DB.relationship('Review',    backref='work', lazy='joined', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    mediation_rounds =  DB.relationship('Mediation', backref='work', lazy='joined', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work_offer):
        self.offer = work_offer

    @classmethod
    def query_by_user(cls, user):
        from rebase.models import WorkOffer, Contractor, Bid, Auction, TicketSet, User
        from rebase.models import BidLimit, TicketSnapshot, Ticket , Organization

        query = cls.query

        if user.is_admin():
            return query

        query_contractor = query.join(cls.offer)
        query_contractor = query_contractor.join(WorkOffer.contractor)
        query_contractor = query_contractor.join(Contractor.user)
        query_contractor = query_contractor.filter(User.id == user.id)

        if user.manager_for_organizations:
            query_manager = query.join(cls.offer)
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

    def allowed_to_be_modified_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_deleted_by(self, user):
        return self.allowed_to_be_created_by(user)

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        elif self.offer.contractor.user == user:
            return True
        elif self.offer.bid and self.offer.bid.auction.organization.id in user.manager_for_organizations:
            return True
        else:
            return False

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        self._machine = WorkStateMachine(self, initial_state=self.state)
        return self._machine

    def start_mediation(self):
        self.mediation_rounds.append(Mediation(self))

    @validates('offer')
    def validate_work_offer(self, field, value):
        if not isinstance(value, WorkOffer):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, WorkOffer))
        return value

    def __repr__(self):
        return '<Work[{}] from Offer[{}]>'.format(self.id, self.offer.id)

class WorkStateMachine(StateMachine):

    def set_state(self, _, new_state):
        self.work.state = new_state.__name__

    def in_progress(self):
        pass

    def blocked(self, reason):
        pass

    def in_review(self):
        from rebase.models.review import Review
        review = Review(self.work)
        DB.session.add(review)

    def in_mediation(self):
        self.work.start_mediation()

    def complete(self):
        pass

    def failed(self):
        pass

    def __init__(self, work_instance, initial_state):
        self.work = work_instance
        StateMachine.__init__(self, initial_state = getattr(self, initial_state))
        self.add_event_transitions('halt_work', {self.in_progress: self.blocked})
        self.add_event_transitions('review', {self.in_progress: self.in_review})
        self.add_event_transitions('mediate', {self.in_review: self.in_mediation})
        self.add_event_transitions('complete', {self.in_review: self.complete, self.in_mediation: self.complete})
        self.add_event_transitions('resume_work', {self.in_mediation: self.in_progress, self.blocked: self.in_progress})
        self.add_event_transitions('fail', {self.in_mediation: self.failed})
