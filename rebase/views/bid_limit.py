from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class BidLimitSchema(RebaseSchema):
    id =              fields.Integer()
    price =           fields.Integer()
    ticket_snapshot = SecureNestedField('TicketSnapshotSchema', only=('id','title'), required=True)
    ticket_set =      SecureNestedField('TicketSetSchema', only=('id',), required=True)

    def make_object(self, data):
        from rebase.models import BidLimit
        return get_or_make_object(BidLimit, data)

serializer = BidLimitSchema(only=('id', 'price', 'ticket_snapshot','ticket_set'), skip_missing=True)

## we want only the id for serialization. for deserialization, we want to be able
## to pass the entire object in order to create a new sub resource
#serializer.declared_fields['ticket_snapshot'].only = 'id'
#serializer.declared_fields['ticket_set'].only = 'id'

deserializer = BidLimitSchema(only=('price','ticket_snapshot'), strict=True)
update_deserializer = BidLimitSchema(only=('price',), strict=True)
