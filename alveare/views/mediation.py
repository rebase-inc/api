import datetime

from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class MediationSchema(AlveareSchema):
    id = fields.Integer()
    dev_answer = fields.String()
    client_answer = fields.String()
    timeout = fields.DateTime()
    state = fields.String()
    work = SecureNestedField('WorkSchema', only='id', required=True)
    arbitration = SecureNestedField('ArbitrationSchema', only='id', default=None)
    foobar = fields.String(required=True)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from alveare.models import Mediation
        return get_or_make_object(Mediation, data)

serializer = MediationSchema(only=('id','work','dev_answer','client_answer','timeout','state','arbitration'), skip_missing=True)
deserializer = MediationSchema(only=('work','state','timeout','dev_answer','client_answer'))

update_deserializer = MediationSchema(only=('state','timeout','dev_answer','client_answer'))
update_deserializer.make_object = lambda data: data

