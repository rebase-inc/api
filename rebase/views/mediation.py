import datetime

from marshmallow import fields

from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class MediationSchema(RebaseSchema):
    id =            fields.Integer()
    dev_answer =    fields.String()
    client_answer = fields.String()
    timeout =       fields.DateTime()
    state =         fields.String()
    work =          SecureNestedField('WorkSchema')
    arbitration =   SecureNestedField('ArbitrationSchema', default=None)
    comments =      SecureNestedField('CommentSchema',      only=('id',), many=True, default=None)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from rebase.models import Mediation
        return get_or_make_object(Mediation, data)


class DevAnswerEventSchema(RebaseSchema):
    dev_answer = fields.String()

    def make_object(self, data):
        return 'dev_answer', data.pop('dev_answer')


class ClientAnswerEventSchema(RebaseSchema):
    client_answer = fields.String()

    def make_object(self, data):
        return 'client_answer', data.pop('client_answer')


class TimeoutEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'timeout'


class TimeoutAnswerEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'timeout_answer'


class AgreeEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'agree'


class ArbitrateEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'arbitrate'


serializer =            MediationSchema()
deserializer =          MediationSchema(strict=True)
update_deserializer =   MediationSchema(only=('id', 'timeout', 'client_answer', 'dev_answer'))
update_deserializer.make_object = lambda data: data

dev_answer_event_deserializer = DevAnswerEventSchema()
client_answer_event_deserializer = ClientAnswerEventSchema()
timeout_event_deserializer = TimeoutEventSchema()
timeout_answer_event_deserializer = TimeoutAnswerEventSchema()
agree_event_deserializer = AgreeEventSchema()
arbitrate_event_deserializer = ArbitrateEventSchema()
