from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class DebitSchema(RebaseSchema):

    id = fields.Integer()
    price = fields.Integer()
    paid = fields.Boolean()
    work = SecureNestedField('WorkSchema')

    @post_load
    def make_debit(self, data):
        from rebase.models import Debit
        return self._get_or_make_object(Debit, data)


serializer = DebitSchema()
deserializer = DebitSchema(only=('work','price'))
update_deserializer = DebitSchema(only=tuple(), context={'raw': True}, strict=True)
