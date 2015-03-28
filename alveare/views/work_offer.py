from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object

class WorkOfferSchema(AlveareSchema):
    #bid = fields.Nested('BidSchema', only='id', required=True)
    id = fields.Integer()
    price = fields.Integer()
    work = fields.Nested('WorkSchema', only='id', default=None)
    contractor = fields.Nested('ContractorSchema', only='id', required=True)
    ticket_snapshot = fields.Nested('TicketSnapshotSchema', only='id', required=True)

    def make_object(self, data):
        from alveare.models import WorkOffer
        return get_or_make_object(WorkOffer, data)

serializer = WorkOfferSchema(only=('id','price','work','ticket_snapshot'), skip_missing=True)
deserializer = WorkOfferSchema(only=('price','work','contractor','ticket_snapshot'), strict=True)

update_deserializer = WorkOfferSchema(only=('price',), strict=True)
update_deserializer.make_object = lambda data: data
