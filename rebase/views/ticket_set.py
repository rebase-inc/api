from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.views.bid_limit import BidLimitSchema


class TicketSetSchema(RebaseSchema):
    id =          fields.Integer()
    bid_limits =  SecureNestedField(BidLimitSchema, exclude=('ticket_set',), only=('id', 'price', 'ticket_snapshot'), many=True)
    auction =     SecureNestedField('AuctionSchema', only=('id',))
    nominations = SecureNestedField('NominationSchema', only=('contractor', 'ticket_set', 'job_fit', 'auction'), many=True)

    @post_load
    def make_ticket_set(self, data):
        from rebase.models import TicketSet
        return self._get_or_make_object(TicketSet, data)


serializer = TicketSetSchema()
deserializer = TicketSetSchema(strict=True)
update_deserializer = TicketSetSchema(context={'raw': True})
