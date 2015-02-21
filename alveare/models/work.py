from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

from .work_offer import WorkOffer
from alveare.common.database import DB
from alveare.common.state import StateMachine, StateModel

class Work(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    state = DB.Column(StateModel)

    review =            DB.relationship('Review',    backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    debit =             DB.relationship('Debit',     backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    credit =            DB.relationship('Credit',    backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    offer =             DB.relationship('WorkOffer', backref='work', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    mediation_rounds =  DB.relationship('Mediation', backref='work', lazy='dynamic', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work_offer):
        self.offer = work_offer

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        if self.state == 'NONE':
            self._machine = MediationStateMachine(self)
        else:
            self._machine = MediationStateMachine(self, resume_state=getattr(StateMachine, self.state))
        return self._machine

    def start_mediation(self):
        self.mediation_rounds.append(Mediation())

    @validates('offer')
    def validate_work_offer(self, field, value):
        if not isinstance(value, WorkOffer):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, WorkOffer))
        return value

    def __repr__(self):
        return '<Work[{}] from Offer[{}]>'.format(self.id, self.offer.id)

class WorkStateMachine(StateMachine):
    def blocked(self):
        self.mediation.state = 'blocked'

    def checking_in(self):
        self.mediation.state = 'checking_in'

    def in_progress(self):
        self.mediation.state = 'in_progress'

    def in_review(self):
        self.mediation.state = 'in_review'

    def complete(self):
        self.mediation.state = 'complete'

    def failed(self):
        self.mediation.state = 'failed'

    def __init__(self, mediation_instance, resume_state=None):
        self.mediation = mediation_instance
        StateMachine.__init__(self, resume_state = resume_state)
        self.add_event_transitions('initialize', {None: self.in_progress})
        self.add_event_transitions('request_check_in', {self.in_progress: self.checking_in})
        self.add_event_transitions('halt_work', {self.in_progress: self.blocked})
        self.add_event_transitions('resume_work', {
            self.checking_in: self.in_progress,
            self.blocked: self.in_progress,
            self.in_review: self.in_progress
        })
        self.add_event_transitions('request_review', {
            self.in_progress: self.in_progress,
            self.blocked: self.in_progress
        })
        self.add_event_transitions('mark_complete', {self.in_review: self.complete})
        self.add_event_transitions('mark_failed', {self.in_review: self.failed})
