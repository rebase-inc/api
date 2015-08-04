from marshmallow import fields
from rebase.common.schema import AlveareSchema

from rebase.views.ticket_set import TicketSetSchema
from rebase.common.database import get_or_make_object

class TermSheetSchema(AlveareSchema):
    id =      fields.Integer()
    legalese = fields.String(required=True)

    def make_object(self, data):
        from rebase.models import TermSheet
        return get_or_make_object(TermSheet, data)

serializer = TermSheetSchema(only=('id', 'legalese'), skip_missing=True)
deserializer = TermSheetSchema(only=('legalese',), strict=True)
update_deserializer = TermSheetSchema(only=('legalese',), strict=True)
