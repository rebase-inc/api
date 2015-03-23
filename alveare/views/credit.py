
from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object

class CreditSchema(AlveareSchema):

    id = fields.Integer()
    work = fields.Nested('WorkSchema', only='id')
    price = fields.Integer()
    paid = fields.Boolean()

    def make_object(self, data):
        from alveare.models import Credit
        return get_or_make_object(Credit, data)

serializer = CreditSchema(only=('id','work','price','paid'))
deserializer = CreditSchema(only=('work','price'))

update_deserializer = CreditSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data
