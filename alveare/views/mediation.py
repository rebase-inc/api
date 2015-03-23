import datetime

from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema

class MediationSchema(AlveareSchema):
    id = fields.Integer()
    dev_answer = fields.String()
    client_answer = fields.String()
    timeout = fields.DateTime()
    state = fields.String()
    work = fields.Nested('WorkSchema', only='id', required=True)
    arbitration = fields.Nested('ArbitrationSchema', only='id', default=None)
    foobar = fields.String(required=True)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from alveare.models import Mediation, Work
        if data.get('id'):
            mediation = Mediation.query.get(data.get('id'))
            if not mediation:
                raise ValueError('No mediation with id {id}'.format(**data))
            return mediation
        mediation = Mediation(data.get('work'), data.get('timeout', datetime.datetime.now()))
        mediation.state = data.get('state', mediation.state)
        mediation.dev_answer = data.get('dev_answer', mediation.dev_answer)
        mediation.client_answer = data.get('client_answer', mediation.client_answer)
        return mediation

serializer = MediationSchema(only=('id','work','dev_answer','client_answer','timeout','state','arbitration'), skip_missing=True)
deserializer = MediationSchema(only=('work','state','timeout','dev_answer','client_answer'))

updater = MediationSchema(only=('state','timeout','dev_answer','client_answer'))
updater.make_object = lambda data: data

