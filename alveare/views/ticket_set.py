from marshmallow import fields
from rebase.common.schema import AlveareSchema

from rebase.views.bid_limit import BidLimitSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class TicketSetSchema(AlveareSchema):
    id =          fields.Integer()
    bid_limits =  SecureNestedField(BidLimitSchema, exclude=('ticket_set',), only=('id', 'price', 'ticket_snapshot'), many=True)
    auction =     SecureNestedField('AuctionSchema', only=('id',))
    nominations = SecureNestedField('NominationSchema', only=('contractor', 'ticket_set'), many=True)

    def make_object(self, data):
        from rebase.models import TicketSet
        return get_or_make_object(TicketSet, data)

serializer = TicketSetSchema(skip_missing=True)
deserializer = TicketSetSchema(strict=True)
update_deserializer = TicketSetSchema()
update_deserializer.make_object = lambda data: data
