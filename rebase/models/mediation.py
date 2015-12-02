from flask.ext.login import current_user
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

import datetime

from rebase.common.database import DB, PermissionMixin
from rebase.common.exceptions import ClientError
from rebase.common.state import StateMachine
from rebase.models.comment import Comment

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

    def __init__(self, work, comment, timeout = datetime.datetime.now() + datetime.timedelta(days=3)):
        self.work = work
        self.timeout = timeout
        Comment(current_user, comment, mediation=self)

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

    allowed_to_be_modified_by = allowed_to_be_created_by
    allowed_to_be_deleted_by = allowed_to_be_created_by

    def allowed_to_be_viewed_by(self, user):
        return self.found(self, user)

    def __repr__(self):
        return '<Mediation[id:{}] >'.format(self.id)

    @validates('work')
    def validate_work(self, field, value):
        if not hasattr(value, 'offer'):
            raise MediationInvalidWork(self, field, self.__tablename__, 'Work type', type(value))
        return value

class MediationStateMachine(StateMachine):
    valid_answers = ['resume_work', 'need_rating', 'fail']

    def set_state(self, _, new_state):
        self.mediation.state = new_state.__name__

    def discussion(self):
        pass

    def waiting_for_client(self, answer, comment):
        if answer not in self.valid_answers:
            raise InvalidMediationAnswer(self, answer, comment)
        self.mediation.dev_answer = answer
        Comment(current_user, comment, mediation=self.mediation)

    def waiting_for_dev(self, answer, comment):
        if answer not in self.valid_answers:
            raise InvalidMediationAnswer(self, answer, comment)
        self.mediation.client_answer = answer
        Comment(current_user, comment, mediation=self.mediation)

    def decision(self, answer, comment):
        Comment(current_user, comment, mediation=self.mediation)
        if hasattr(self.mediation, 'client_answer'):
            self.mediation.dev_answer = answer
        else:
            self.mediation.client_answer = answer

        if self.mediation.client_answer == self.mediation.dev_answer:
            self.send('agree')
        else:
            self.send('arbitrate')

    def timed_out(self):
        if hasattr(self, 'client_answer'):
            self.send('timeout_answer', self.mediation.client_answer)
        else:
            self.send('timeout_answer', self.mediation.dev_answer)

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

class InvalidMediationAnswer(ClientError):
    error_message = 'Invalid answer: {invalid_answer} with comment: "{comment}"\nValid answers: {valid_answers}'

    def __init__(self, machine, invalid_answer, comment):
        super().__init__(
            code=400,
            message=self.error_message.format(
                invalid_answer=invalid_answer,
                comment=comment,
                valid_answers=MediationStateMachine.valid_answers
            ),
            more_data= {
                'mediation': {
                    'id': machine.mediation.id,
                    'state': machine.mediation.state,
                    'client_answer': machine.mediation.client_answer,
                    'dev_answer': machine.mediation.dev_answer,
                },
                'ticket': {
                    'id': machine.mediation.work.offer.ticket_snapshot.ticket.id,
                    'title': machine.mediation.work.offer.ticket_snapshot.title
                }
            }
        )

class MediationInvalidWork(ClientError):
    error_message = '{} field on {} must be {}, not {}'
    
    def __init__(self, mediation, field, model, field_type, field_type_value):
        super().__init__(
            message=self.error_message.format(field, model, field_type, field_type_value),
            more_data={
                'work': {
                    'id': mediation.work.id,
                },
                'ticket': {
                    'id': mediation.work.offer.ticket_snapshot.ticket_id,
                    'title': mediation.work.offer.ticket_snapshot.title,
                },
                'contract': {
                    'id': mediation.work.offer.bid.contract.id,
                }
            }
        )
