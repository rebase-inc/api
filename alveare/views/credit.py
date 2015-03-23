

from marshmallow import fields
from alveare.common.schema import AlveareSchema

class CreditSchema(AlveareSchema):
    id = fields.Integer()
    work = fields.Nested('WorkSchema', only='id')
    price = fields.Integer()
    paid = fields.Boolean()

    def make_object(self, data):
        from alveare.models import Credit
        return Credit(**data)

serializer = CreditSchema(only=('id','work','price','paid'))
deserializer = CreditSchema(only=('work','price'))

updater = CreditSchema(only=('work','price','paid'))
updater.make_object = lambda data: data
