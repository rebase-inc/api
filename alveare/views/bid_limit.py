from marshmallow import fields, Schema

class BidLimitSchema(Schema):
    id =              fields.Integer()
    price =           fields.Integer()
    ticket_snapshot = fields.Nested('TicketSnapshotSchema', required=True)

    def make_object(self, data):
        from alveare.models import BidLimit
        if data.get('id'):
            bid_limit = BidLimit.query.get(data.get('id'))
            if not bid_limit:
                raise ValueError('No bid_limit with id {id}'.format(**data))
            return bid_limit
        return BidLimit(**data)

serializer = BidLimitSchema(only=('id', 'price', 'snapshot'), skip_missing=True)
deserializer = BidLimitSchema(only=('price','ticket_snapshot'), strict=True)
