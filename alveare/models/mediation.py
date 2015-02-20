from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

import sys
import datetime

from alveare.common.database import DB
from alveare.common.state import StateMachine, StateModel, RUNNER

class MediationStateMachine(StateMachine):
    def discussion(self):
        self.mediation.state = 'discussion'
        print('in discussion')

    def waiting_for_client(self):
        self.mediation.state = 'waiting_for_client'
        print('in waiting_for_client')

    def waiting_for_dev(self):
        self.mediation.state = 'waiting_for_dev'
        print('in waiting_for_dev')

    def decision(self):
        self.mediation.state = 'decision'
        print('in decision')

    def timed_out(self):
        self.mediation.state = 'timed_out'
        print('timed out!')

    def agreement(self):
        self.mediation.state = 'agreement'
        print('in agreement')

    def arbitration(self):
        self.mediation.state = 'arbitration'
        print('in arbitration!')

    def __init__(self, mediation_instance, resume_state=None):
        self.mediation = mediation_instance
        StateMachine.__init__(self, resume_state = resume_state)
        self.add_event('initialize', {None: self.discussion})
        self.add_event('dev_answer', {self.discussion: self.waiting_for_client, self.waiting_for_dev:self.decision})
        self.add_event('client_answer', {self.discussion:self.waiting_for_dev, self.waiting_for_client:self.decision})
        self.add_event('timeout', {self.waiting_for_client:self.timed_out, self.waiting_for_dev:self.timed_out})
        self.add_event('timeout_answer', {self.timed_out:self.decision})
        self.add_event('agree', {self.decision:self.agreement})
        self.add_event('enter_arbitration', {self.decision:self.arbitration})

class Mediation(DB.Model):
    id =            DB.Column(DB.Integer, primary_key=True)
    dev_answer =    DB.Column(DB.Integer, nullable=True)
    client_answer = DB.Column(DB.Integer, nullable=True)
    timeout =       DB.Column(DB.DateTime, nullable=False)
    work_id =       DB.Column(DB.Integer, DB.ForeignKey('work.id', ondelete='CASCADE'), nullable=False)
    state =         DB.Column(StateModel, nullable=False, default='NONE')

    arbitration =   DB.relationship('Arbitration', backref='mediation', uselist=False, cascade='all, delete-orphan', passive_deletes=True)

    @hybrid_property
    def machine(self):
        if hasattr(self, '_machine'):
            return self._machine
        if self.state == 'NONE':
            self._machine = MediationStateMachine(self)
        else:
            machine = MediationStateMachine(self, resume_state=getattr(StateMachine, self.state))
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
