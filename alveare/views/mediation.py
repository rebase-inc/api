import datetime

from marshmallow import fields, Schema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema

class MediationSchema(Schema):
    id = fields.Integer()
    dev_answer = fields.String()
    client_answer = fields.String()
    timeout = fields.DateTime()
    state = fields.String()
    work = fields.Nested('WorkSchema', only='id', required=True)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from alveare.models import Mediation, Work
        mediation = Mediation(data.get('work'), data.get('timeout', datetime.datetime.now()))
        mediation.state = data.get('state', mediation.state)
        mediation.dev_answer = data.get('dev_answer', mediation.dev_answer)
        mediation.client_answer = data.get('client_answer', mediation.client_answer)
        return mediation

serializer = MediationSchema(only=('id','work','dev_answer','client_answer','timeout','state'))
deserializer = MediationSchema(only=('work','state','timeout','dev_answer','client_answer'))

updater = MediationSchema(only=('state','timeout','dev_answer','client_answer'))
updater.make_object = lambda data: data

