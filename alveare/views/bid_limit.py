from marshmallow import fields, Schema

class BidLimitSchema(Schema):
    id =       fields.Integer()
    price =    fields.Integer()
    auction =  fields.Nested('AuctionSchema', only='id')
    snapshot = fields.Nested('TicketSnapshotSchema', only='id', required=True)

    def make_object(self, data):
        from alveare.models import TicketSet
        if data.get('id'):
            ticket_set = TicketSet.query.get(data.get('id'))
            if not ticket_set:
                raise ValueError('No ticket_set with id {id}'.format(**data))
            return ticket_set
        return TicketSet(**data)

serializer = BidLimitSchema(only=('id', 'price', 'auction', 'snapshot'), skip_missing=True)
deserializer = BidLimitSchema(only=('price','snapshot'), strict=True)
