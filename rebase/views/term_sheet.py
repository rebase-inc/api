from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema

from rebase.views.ticket_set import TicketSetSchema
from rebase.common.database import get_or_make_object

class TermSheetSchema(RebaseSchema):
    id =      fields.Integer()
    legalese = fields.String()

    @post_load
    def make_term_sheet(self, data):
        from rebase.models import TermSheet
        return self._get_or_make_object(TermSheet, data)

serializer = TermSheetSchema(only=('id', 'legalese'))
deserializer = TermSheetSchema(only=('id', 'legalese',), strict=True)
update_deserializer = TermSheetSchema(only=('legalese',), strict=True)
