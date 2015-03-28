from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views.bid_limit import BidLimitSchema
from alveare.common.database import get_or_make_object

class TicketSetSchema(AlveareSchema):
    id =          fields.Integer()
    bid_limits =  fields.Nested(BidLimitSchema, exclude=('ticket_set',), many=True)
    auction =     fields.Nested('AuctionSchema', only=('id',))
    nominations = fields.Nested('NominationSchema', only=('contractor', 'ticket_set'), many=True)
    #organization = fields.Nested('OrganizationSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import TicketSet
        return get_or_make_object(TicketSet, data)

serializer = TicketSetSchema(only=('id', 'bid_limits','auction'), skip_missing=True)
deserializer = TicketSetSchema(only=('bid_limits',), strict=True)
update_deserializer = TicketSetSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data
