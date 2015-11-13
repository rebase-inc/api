from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class TicketSnapshotSchema(RebaseSchema):
    id =          fields.Integer()
    title =       fields.String()
    date =        fields.DateTime()
    ticket =      SecureNestedField('TicketSchema', only=('id','title', 'created', 'skill_requirement', 'comments','project'))
    bid_limit =   SecureNestedField('BidLimitSchema', only=('id','ticket_set'))

    def make_object(self, data):
        from rebase.models import TicketSnapshot
        return get_or_make_object(TicketSnapshot, data)

serializer = TicketSnapshotSchema(skip_missing=True)

deserializer = TicketSnapshotSchema(only=('id', 'ticket'), skip_missing=True,  strict=True)
update_deserializer = TicketSnapshotSchema()
update_deserializer.make_object = lambda data: data
