import datetime

from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class MediationSchema(RebaseSchema):
    id =            fields.Integer()
    created =       fields.DateTime()
    ended =         fields.DateTime()
    dev_answer =    fields.String()
    client_answer = fields.String()
    timeout =       fields.DateTime()
    state =         fields.String()
    work =          SecureNestedField('WorkSchema')
    arbitration =   SecureNestedField('ArbitrationSchema', default=None)
    comments =      SecureNestedField('CommentSchema', only=('id', 'content', 'created', 'user', 'type'), many=True, default=None)

    @post_load
    def make_mediation(self, data):
        ''' This is an admin only procedure '''
        from rebase.models import Mediation
        return self._get_or_make_object(Mediation, data)


class DevAnswerEventSchema(RebaseSchema):
    answer = fields.String()
    comment = fields.String()

    @post_load
    def make_dev_answer(self, data):
        return 'dev_answer', data


class ClientAnswerEventSchema(RebaseSchema):
    answer = fields.String()
    comment = fields.String()

    @post_load
    def make_client_answer(self, data):
        return 'client_answer', data


class TimeoutEventSchema(RebaseSchema):

    @post_load
    def make_timeout(self, data):
        return 'timeout'


class TimeoutAnswerEventSchema(RebaseSchema):

    @post_load
    def make_timeout_answer(self, data):
        return 'timeout_answer'


class AgreeEventSchema(RebaseSchema):

    @post_load
    def make_agree(self, data):
        return 'agree'


class ArbitrateEventSchema(RebaseSchema):

    @post_load
    def make_arbitrate(self, data):
        return 'arbitrate'


serializer =            MediationSchema()
deserializer =          MediationSchema(strict=True)
update_deserializer =   MediationSchema(only=('id', 'timeout', 'client_answer', 'dev_answer'), context={'raw': True})

dev_answer_event_deserializer = DevAnswerEventSchema()
client_answer_event_deserializer = ClientAnswerEventSchema()
timeout_event_deserializer = TimeoutEventSchema()
timeout_answer_event_deserializer = TimeoutAnswerEventSchema()
agree_event_deserializer = AgreeEventSchema()
arbitrate_event_deserializer = ArbitrateEventSchema()
