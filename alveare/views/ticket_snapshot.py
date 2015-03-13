from marshmallow import fields, Schema

class TicketSnapshotSchema(Schema):
    id =          fields.Integer()
    title =       fields.String()
    description = fields.String()
    date =        fields.DateTime()
    ticket =      fields.Nested('TicketSchema', only='id', required=True)
    bid_limit =   fields.Nested('BidLimitSchema', only='id')

    def make_object(self, data):
        from alveare.models import TicketSnapshot
        ticket_snapshot_id = data.pop('id', None)
        if ticket_snapshot_id:
            ticket_snapshot = TicketSnapshot.query.get(ticket_snapshot_id)
            if not ticket_snapshot:
                raise ValueError('No ticket snapshot with id {id}'.format(**data))
            return ticket_snapshot
        return TicketSnapshot(**data)

serializer = TicketSnapshotSchema(skip_missing=True)

deserializer = TicketSnapshotSchema(only=('ticket',), strict=True)
deserializer.declared_fields['ticket'].only = None
deserializer.declared_fields['bid_limit'].only = None
