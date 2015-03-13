from marshmallow import fields, Schema

from alveare.views.ticket_set import TicketSetSchema

class TermSheetSchema(Schema):
    id =      fields.Integer()
    legalese = fields.String(required=True)

    def make_object(self, data):
        from alveare.models import TermSheet
        if data.get('id'):
            term_sheet = TermSheet.query.get(data.get('id'))
            if not term_sheet:
                raise ValueError('No term_sheet with id {id}'.format(**data))
            return term_sheet
        return TermSheet(**data)

serializer = TermSheetSchema(only=('id', 'legalese'), skip_missing=True)
deserializer = TermSheetSchema(only=('legalese',), strict=True)
update_deserializer = TermSheetSchema(only=('legalese',), strict=True)
