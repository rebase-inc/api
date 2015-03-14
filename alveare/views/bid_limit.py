from marshmallow import fields, Schema
from alveare.common.resource import get_or_make_object, update_object

class BidLimitSchema(Schema):
    id =              fields.Integer()
    price =           fields.Integer()
    ticket_snapshot = fields.Nested('TicketSnapshotSchema', only=('id',))
    ticket_set =      fields.Nested('TicketSetSchema', only=('id',), required=True)

    def make_object(self, data):
        from alveare.models import BidLimit
        return get_or_make_object(BidLimit, data)

    def _update_object(self, data):
        from alveare.models import BidLimit
        return update_object(BidLimit, data)

serializer = BidLimitSchema(only=('id', 'price', 'ticket_snapshot','ticket_set'), skip_missing=True)

## we want only the id for serialization. for deserialization, we want to be able
## to pass the entire object in order to create a new sub resource
#serializer.declared_fields['ticket_snapshot'].only = 'id'
#serializer.declared_fields['ticket_set'].only = 'id'

deserializer = BidLimitSchema(only=('price','ticket_snapshot'), strict=True)
update_deserializer = BidLimitSchema(only=('price','ticket_snapshot'), strict=True)