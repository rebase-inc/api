import datetime

from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema, SecureNestedField

from rebase.views import NamespacedSchema
from rebase.views.comment import CommentSchema

class ArbitrationSchema(RebaseSchema):
    id = fields.Integer()
    mediation = SecureNestedField('MediationSchema', only='id', required=True)

    @post_load
    def make_arbitration(self, data):
        ''' This is an admin only procedure '''
        from rebase.models import Arbitration
        return self._get_or_make_object(Arbitration, data)

serializer = ArbitrationSchema(only=('id','mediation'))
deserializer = ArbitrationSchema(only=('mediation',))
update_deserializer = ArbitrationSchema(only=tuple(), context={'raw': True}, strict=True)

