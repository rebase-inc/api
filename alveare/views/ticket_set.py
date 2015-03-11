from marshmallow import fields, Schema

from alveare.views.bid_limit import BidLimitSchema

class TicketSetSchema(Schema):
    id =               fields.Integer()
    bid_limits =       fields.Nested(BidLimitSchema, exclude=('ticket_set',), many=True)

    def make_object(self, data):
        from alveare.models import TicketSet
        if data.get('id'):
            ticket_set = TicketSet.query.get(data.get('id'))
            if not ticket_set:
                raise ValueError('No ticket_set with id {id}'.format(**data))
            return ticket_set
        return TicketSet(**data)

serializer = TicketSetSchema(only=('id', 'bid_limits'), skip_missing=True)
deserializer = TicketSetSchema(only=('bid_limits',), strict=True)
