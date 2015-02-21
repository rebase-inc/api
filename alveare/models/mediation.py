from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

import sys
import datetime

from alveare.common.database import DB
from alveare.common.state import StateMachine, StateModel

class Mediation(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    dev_answer =    DB.Column(DB.Integer, nullable=True)
    client_answer = DB.Column(DB.Integer, nullable=True)
    timeout =       DB.Column(DB.DateTime, nullable=False)
    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    state =         DB.Column(StateModel, nullable=False, default='discussion')

    arbitration =   DB.relationship('Arbitration', backref='mediation', uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        self._machine = MediationStateMachine(self, initial_state=self.state)
        return self._machine

    def __init__(self, work, timeout = datetime.datetime.now() + datetime.timedelta(days=3)):
        self.work = work
        self.timeout = timeout

    def __repr__(self):
        return '<Mediation[id:{}] >'.format(self.id)

    @validates('work')
    def validate_work_offer(self, field, value):
        if not hasattr(value, 'offer'):
            raise ValueError('{} field on {} must be {}'.format(field, self.__tablename__, 'Work type'))
        return value

class MediationStateMachine(StateMachine):

    def set_state(self, new_state):
        self.mediation.state = new_state.__name__

    def discussion(self):
        #print('in {} state'.format(self._current_state.__name__))
        pass

    def waiting_for_client(self):
        pass

    def waiting_for_dev(self):
        pass

    def decision(self):
        pass

    def timed_out(self):
        pass

    def agreement(self):
        pass

    def arbitration(self):
        pass

    def __init__(self, mediation_instance, initial_state):
        self.mediation = mediation_instance
        StateMachine.__init__(self, initial_state = getattr(self, initial_state))
        self.add_event_transitions('initialize', {None: self.discussion})
        self.add_event_transitions('dev_answer', {self.discussion: self.waiting_for_client, self.waiting_for_dev:self.decision})
        self.add_event_transitions('client_answer', {self.discussion:self.waiting_for_dev, self.waiting_for_client:self.decision})
        self.add_event_transitions('timeout', {self.waiting_for_client:self.timed_out, self.waiting_for_dev:self.timed_out})
        self.add_event_transitions('timeout_answer', {self.timed_out:self.decision})
        self.add_event_transitions('agree', {self.decision:self.agreement})
        self.add_event_transitions('enter_arbitration', {self.decision:self.arbitration})
