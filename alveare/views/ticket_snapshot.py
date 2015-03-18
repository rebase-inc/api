from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object

class TicketSnapshotSchema(Schema):
    id =          fields.Integer()
    title =       fields.String()
    description = fields.String()
    date =        fields.DateTime()
    ticket =      fields.Nested('TicketSchema', only=('id',), required=True)
    bid_limit =   fields.Nested('BidLimitSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import TicketSnapshot
        return get_or_make_object(TicketSnapshot, data)

serializer = TicketSnapshotSchema(skip_missing=True)

deserializer = TicketSnapshotSchema(only=('ticket',), strict=True)
#deserializer.declared_fields['ticket'].only = None
#deserializer.declared_fields['bid_limit'].only = None
