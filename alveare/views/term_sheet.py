from marshmallow import fields, Schema

from alveare.views.ticket_set import TicketSetSchema
from alveare.common.database import get_or_make_object

class TermSheetSchema(Schema):
    id =      fields.Integer()
    legalese = fields.String(required=True)

    def make_object(self, data):
        from alveare.models import TermSheet
        return get_or_make_object(TermSheet, data)

serializer = TermSheetSchema(only=('id', 'legalese'), skip_missing=True)
deserializer = TermSheetSchema(only=('legalese',), strict=True)
update_deserializer = TermSheetSchema(only=('legalese',), strict=True)
