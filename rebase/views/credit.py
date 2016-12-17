from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema, SecureNestedField


class CreditSchema(RebaseSchema):

    id = fields.Integer()
    price = fields.Integer()
    paid = fields.Boolean()
    work = SecureNestedField('WorkSchema')

    @post_load
    def make_credit(self, data):
        from rebase.models import Credit
        return self._get_or_make_object(Credit, data)

serializer = CreditSchema()
deserializer = CreditSchema(only=('work','price'))

update_deserializer = CreditSchema(only=tuple(), context={'raw': True}, strict=True)
