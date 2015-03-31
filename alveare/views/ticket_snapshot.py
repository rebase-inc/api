from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class TicketSnapshotSchema(AlveareSchema):
    id =          fields.Integer()
    title =       fields.String()
    description = fields.String()
    date =        fields.DateTime()
    ticket =      SecureNestedField('TicketSchema', only=('id',), required=True)
    bid_limit =   SecureNestedField('BidLimitSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import TicketSnapshot
        return get_or_make_object(TicketSnapshot, data)

serializer = TicketSnapshotSchema(skip_missing=True)

deserializer = TicketSnapshotSchema(only=('ticket',), strict=True)
update_deserializer = TicketSnapshotSchema()
update_deserializer.make_object = lambda data: data
