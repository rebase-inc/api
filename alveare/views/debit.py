from marshmallow import fields, Schema

from alveare.common.database import get_or_make_object

class DebitSchema(Schema):
    id = fields.Integer()
    work = fields.Nested('WorkSchema', only='id')
    price = fields.Integer()
    paid = fields.Boolean()

    def make_object(self, data):
        from alveare.models import Debit
        return get_or_make_object(Debit, data)

serializer = DebitSchema(only=('id','work','price','paid'))
deserializer = DebitSchema(only=('work','price'))

update_deserializer = DebitSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data
