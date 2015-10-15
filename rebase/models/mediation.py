from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

import sys
import datetime

from rebase.common.database import DB, PermissionMixin, query_by_user_or_id
from rebase.common.query import query_from_class_to_user
from rebase.common.state import StateMachine

class Mediation(DB.Model, PermissionMixin):
    __pluralname__ = 'mediations'

    id =            DB.Column(DB.Integer, primary_key=True)
    dev_answer =    DB.Column(DB.String, nullable=True)
    client_answer = DB.Column(DB.String, nullable=True)
    timeout =       DB.Column(DB.DateTime, nullable=False)
    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    state =         DB.Column(DB.String, nullable=False, default='discussion')

    arbitration =   DB.relationship('Arbitration', backref='mediation', uselist=False, cascade='all, delete-orphan', passive_deletes=True)
    comments =      DB.relationship('Comment', backref='mediation', lazy='joined', cascade='all, delete-orphan', passive_deletes=True)

    def __init__(self, work, timeout = datetime.datetime.now() + datetime.timedelta(days=3)):
        self.work = work
        self.timeout = timeout

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        self._machine = MediationStateMachine(self, initial_state=self.state)
        return self._machine

    @classmethod
    def setup_queries(cls, models):
        cls.as_contractor_path = [
            models.Work,
            models.WorkOffer,
            models.Contractor,
        ]

        cls.as_manager_path = [
            models.Work,
            models.WorkOffer,
            models.TicketSnapshot,
            models.Ticket,
            models.Project,
            models.Organization,
            models.Manager,
        ]

    def allowed_to_be_created_by(self, user):
        return user.is_admin()

    def allowed_to_be_modified_by(self, user):
        return user.is_admin()

    def allowed_to_be_deleted_by(self, user):
        return user.is_admin()

    def allowed_to_be_viewed_by(self, user):
        if user.is_admin():
            return True
        return self.role_to_query_fn(user)(user).filter(Mediation.id==self.id).first()

    def __repr__(self):
        return '<Mediation[id:{}] >'.format(self.id)

    @validates('work')
    def validate_work(self, field, value):
        if not hasattr(value, 'offer'):
            raise ValueError('{} field on {} must be {}, not {}'.format(field, self.__tablename__, 'Work type', type(value)))
        return value

class MediationStateMachine(StateMachine):
    valid_answers = ['resume_work', 'complete', 'fail']

    def set_state(self, _, new_state):
        self.mediation.state = new_state.__name__

    def discussion(self):
        pass

    def waiting_for_client(self, dev_answer):
        if dev_answer not in self.valid_answers:
            raise ValueError('Invalid dev answer')
        self.mediation.dev_answer = dev_answer

    def waiting_for_dev(self, client_answer):
        if client_answer not in self.valid_answers:
            raise ValueError('Invalid dev answer')
        self.mediation.client_answer = client_answer

    def decision(self, remaining_answer):
        if hasattr(self, 'client_answer'):
            self.mediation.dev_answer = remaining_answer
        else:
            self.mediation.client_answer = remaining_answer

        if self.mediation.client_answer == self.mediation.dev_answer:
            self.send('agree')
        else:
            self.send('arbitrate')

    def timed_out(self):
        if hasattr(self, 'client_answer'):
            self.send('timeout_answer', self.mediation.client_answer)
        else:
            self.send('timeout_answer', self.mediation.dev_answer)
        pass

    def agreement(self):
        self.mediation.work.machine.send(self.mediation.dev_answer)

    def arbitration(self):
        pass

    def __init__(self, mediation_instance, initial_state):
        self.mediation = mediation_instance
        StateMachine.__init__(self, initial_state = getattr(self, initial_state))

        self.add_event_transitions('dev_answer',    {
            self.discussion:        self.waiting_for_client,
            self.waiting_for_dev:   self.decision
        })
        self.add_event_transitions('client_answer', {
            self.discussion:            self.waiting_for_dev,
            self.waiting_for_client:    self.decision
        })
        self.add_event_transitions('timeout',       {
            self.waiting_for_client:    self.timed_out,
            self.waiting_for_dev:       self.timed_out
        })
        self.add_event_transitions('timeout_answer',{
            self.timed_out: self.decision
        })
        self.add_event_transitions('agree',         {
            self.decision:  self.agreement
        })
        self.add_event_transitions('arbitrate',     {
            self.decision:  self.arbitration
        })
