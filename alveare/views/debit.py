
from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class DebitSchema(AlveareSchema):

    id = fields.Integer()
    price = fields.Integer()
    paid = fields.Boolean()
    work = SecureNestedField('WorkSchema', only='id')

    def make_object(self, data):
        from alveare.models import Debit
        return get_or_make_object(Debit, data)

serializer = DebitSchema(only=('id','work','price','paid'))
deserializer = DebitSchema(only=('work','price'))

update_deserializer = DebitSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data
