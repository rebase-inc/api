from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views.ticket_set import TicketSetSchema
from alveare.common.database import get_or_make_object

class ContractSchema(AlveareSchema):
    id =  fields.Integer()
    bid = fields.Nested('BidSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import Contract
        return get_or_make_object(Contract, data)

serializer = ContractSchema(only=('id',), skip_missing=True)
deserializer = ContractSchema(only=('bid',), strict=True)
update_deserializer = ContractSchema()
