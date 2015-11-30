from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema

from rebase.views.ticket_set import TicketSetSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class ContractSchema(RebaseSchema):
    id =  fields.Integer()
    bid = SecureNestedField('BidSchema', exclude=('contract',))

    @post_load
    def make_contract(self, data):
        from rebase.models import Contract
        return get_or_make_object(Contract, data)

serializer = ContractSchema()
deserializer = ContractSchema(only=('bid',), strict=True)
update_deserializer = ContractSchema(only=('id',), strict=True)
update_deserializer.make_object = lambda data: data
