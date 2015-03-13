from marshmallow import fields, Schema

class TicketSnapshotSchema(Schema):
    id =          fields.Integer()
    title =       fields.String()
    description = fields.String()
    date =        fields.DateTime()
    ticket =      fields.Nested('TicketSchema', only='id', required=True)
    #bid_limit = fields.Nested('BidLimitSchema')
    #ticket = fields.Nested('TicketSchema')

    def make_object(self, data):
        from alveare.models import TicketSnapshot
        if 'id' in data:
            ticket_snapshot = TicketSnapshot.query.get(data.get('id'))
            if not ticket_snapshot:
                raise ValueError('No ticket snapshot with id {id}'.format(**data))
            return ticket_snapshot
        return TicketSnapshot(**data)

serializer = TicketSnapshotSchema(only=('id','ticket','title','description','date'), skip_missing=True)
deserializer = TicketSnapshotSchema(only=('ticket',), strict=True)
