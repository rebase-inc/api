from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema, SecureNestedField


class ContractSchema(RebaseSchema):
    id =  fields.Integer()
    bid = SecureNestedField('BidSchema', exclude=('contract',))

    @post_load
    def make_contract(self, data):
        from rebase.models import Contract
        return self._get_or_make_object(Contract, data)

serializer = ContractSchema()
deserializer = ContractSchema(only=('bid',), strict=True)
update_deserializer = ContractSchema(only=('id',), context={'raw': True}, strict=True)
