from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class TicketSnapshotSchema(RebaseSchema):

    id =          fields.Integer()
    title =       fields.String()
    date =        fields.DateTime()
    ticket =      SecureNestedField('TicketSchema')
    bid_limit =   SecureNestedField('BidLimitSchema', only=('id','ticket_set'))

    @post_load
    def make_ticket_snapshot(self, data):
        from rebase.models import TicketSnapshot
        return self._get_or_make_object(TicketSnapshot, data)


serializer = TicketSnapshotSchema()
deserializer = TicketSnapshotSchema(strict=True)
update_deserializer = TicketSnapshotSchema(context={'raw': True})
