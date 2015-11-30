from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class CreditSchema(RebaseSchema):

    id = fields.Integer()
    price = fields.Integer()
    paid = fields.Boolean()
    work = SecureNestedField('WorkSchema', only='id')

    @post_load
    def make_credit(self, data):
        from rebase.models import Credit
        return get_or_make_object(Credit, data)

serializer = CreditSchema(only=('id','work','price','paid'))
deserializer = CreditSchema(only=('work','price'))

update_deserializer = CreditSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data
