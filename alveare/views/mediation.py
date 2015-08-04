import datetime

from marshmallow import fields

from rebase.common.schema import AlveareSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class MediationSchema(AlveareSchema):
    id =            fields.Integer()
    dev_answer =    fields.String()
    client_answer = fields.String()
    timeout =       fields.DateTime()
    state =         fields.String()
    work =          SecureNestedField('WorkSchema',         only='id', required=True)
    arbitration =   SecureNestedField('ArbitrationSchema',  only='id', default=None)
    comments =      SecureNestedField('CommentSchema',      only=('id',), many=True, default=None)

    def make_object(self, data):
        ''' This is an admin only procedure '''
        from rebase.models import Mediation
        return get_or_make_object(Mediation, data)

serializer =            MediationSchema(skip_missing=True)
deserializer =          MediationSchema(strict=True)
update_deserializer =   MediationSchema()
update_deserializer.make_object = lambda data: data

