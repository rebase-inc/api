from marshmallow import fields, Schema

class TicketSnapshotSchema(Schema):
    id = fields.Integer()
    title = fields.String()
    description = fields.String()
    date = fields.DateTime()
    #bid_limit = fields.Nested('BidLimitSchema')
    #ticket = fields.Nested('TicketSchema')

    def make_object(self, data):
        from alveare.models import TicketSnapshot
        if data.get('id'):
            ticket_snapshot = TicketSnapshot.query.get(data.get('id'))
            if not ticket_snapshot:
                raise ValueError('No ticket snapshot with id {id}'.format(**data))
            return ticket_snapshot
        return TicketSnapshot(**data)

serializer = TicketSnapshotSchema(only=('id','title','description','date'), skip_missing=True)
