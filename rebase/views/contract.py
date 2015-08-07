from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.views.ticket_set import TicketSetSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class ContractSchema(RebaseSchema):
    id =  fields.Integer()
    bid = SecureNestedField('BidSchema', only=('id',))

    def make_object(self, data):
        from rebase.models import Contract
        return get_or_make_object(Contract, data)

serializer = ContractSchema(only=('id',), skip_missing=True)
deserializer = ContractSchema(only=('bid',), strict=True)
update_deserializer = ContractSchema()