from marshmallow import fields, Schema

class BidLimitSchema(Schema):
    id =              fields.Integer()
    price =           fields.Integer()
    ticket_snapshot = fields.Nested('TicketSnapshotSchema', exclude=('bid_limit',))
    ticket_set =      fields.Nested('TicketSetSchema', exclude=('bid_limit',), required=True)

    def make_object(self, data):
        from alveare.models import BidLimit
        if data.get('id'):
            bid_limit = BidLimit.query.get(data.get('id'))
            if not bid_limit:
                raise ValueError('No bid_limit with id {id}'.format(**data))
            return bid_limit
        return BidLimit(**data)

serializer = BidLimitSchema(only=('id', 'price', 'ticket_snapshot','ticket_set'), skip_missing=True)

# we want only the id for serialization. for deserialization, we want to be able
# to pass the entire object in order to create a new sub resource
serializer.declared_fields['ticket_snapshot'].only = 'id'
serializer.declared_fields['ticket_set'].only = 'id'

deserializer = BidLimitSchema(only=('price','ticket_snapshot'), strict=True)
update_deserializer = BidLimitSchema(only=('price','ticket_snapshot'), strict=True)
