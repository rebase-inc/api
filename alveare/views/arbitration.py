import datetime

from marshmallow import fields, Schema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema
from alveare.common.database import get_or_make_object, update_object

class ArbitrationSchema(Schema):
    id = fields.Integer()
    mediation = fields.Nested('MediationSchema', only='id', required=True)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from alveare.models import Arbitration
        return get_or_make_object(Arbitration, data)

serializer = ArbitrationSchema(only=('id','mediation'))
deserializer = ArbitrationSchema(only=('mediation',))
update_deserializer = ArbitrationSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data 

