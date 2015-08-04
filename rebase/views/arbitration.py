import datetime

from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.views import NamespacedSchema
from rebase.views.comment import CommentSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class ArbitrationSchema(RebaseSchema):
    id = fields.Integer()
    mediation = SecureNestedField('MediationSchema', only='id', required=True)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from rebase.models import Arbitration
        return get_or_make_object(Arbitration, data)

serializer = ArbitrationSchema(only=('id','mediation'))
deserializer = ArbitrationSchema(only=('mediation',))
update_deserializer = ArbitrationSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data

