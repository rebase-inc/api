from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views.ticket_set import TicketSetSchema

class ContractSchema(AlveareSchema):
    id =  fields.Integer()
    bid = fields.Nested('BidSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import Contract
        if data.get('id'):
            contract = Contract.query.get(data.get('id'))
            if not contract:
                raise ValueError('No contract with id {id}'.format(**data))
            return contract
        return Contract(**data)

serializer = ContractSchema(only=('id',), skip_missing=True)
deserializer = ContractSchema(only=('bid',), strict=True)
update_deserializer = ContractSchema()
