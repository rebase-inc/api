from os.path import join

from flask import current_app
from sqlalchemy.orm import validates, reconstructor
from sqlalchemy.ext.hybrid import hybrid_property

from .work_offer import WorkOffer
from .mediation import Mediation
from rebase.common.database import DB, PermissionMixin
from rebase.common.state import StateMachine
from rebase.git.repo import Repo

class Work(DB.Model, PermissionMixin):
    __pluralname__ = 'works'

    id =    DB.Column(DB.Integer, primary_key=True)
    state = DB.Column(DB.String, nullable=False, default='in_progress')
    branch = DB.Column(DB.String, nullable=False)

    debit =             DB.relationship('Debit',     backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    credit =            DB.relationship('Credit',    backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    offer =             DB.relationship('WorkOffer', backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    review =            DB.relationship('Review',    backref='work', lazy='joined', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    mediations =        DB.relationship('Mediation', backref='work', lazy='joined', cascade='all, delete-orphan', passive_deletes=True, order_by='Mediation.id')

    _clone = 'git clone -b {branch} --single-branch {url}'

    def __init__(self, work_offer):
        self.offer = work_offer
        self.branch = current_app.config['WORK_BRANCH_NAME'](
            contractor_id=self.offer.contractor_id,
            auction_id=self.offer.bid.auction_id
        )
        project = self.offer.ticket_snapshot.ticket.project
        repo = Repo(project)
        repo.create_branch(self.branch)

    @reconstructor
    def init(self):
        self.clone = Work._clone.format(
            branch=self.branch,
            url=self.offer.ticket_snapshot.ticket.project.work_repo.url
        )

    @classmethod
    def setup_queries(cls, models):
        cls.as_owner_path = [
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Owner,
        ]
        cls.as_contractor_path = [
            models.WorkOffer,
            models.Bid,
            models.Contractor,
        ]
        cls.as_manager_path = [
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Manager
        ]

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        elif self.offer.contractor.user == user:
            return True
        elif self.offer.bid and self.offer.bid.auction.organization.id in user.manager_for_projects:
            return True
        else:
            return False

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        self._machine = WorkStateMachine(self, initial_state=self.state)
        return self._machine

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
        pass

    def in_mediation(self):
        Mediation(self.work)

    def complete(self):
        from rebase.models import Review, Debit, Credit
        review = Review(self.work)
        DB.session.add(review)
        Debit(self.work, int(self.work.offer.price*current_app.config['REVENUE_FACTOR']))
        Credit(self.work, self.work.offer.price)

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
