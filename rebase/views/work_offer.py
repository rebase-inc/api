from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class WorkOfferSchema(RebaseSchema):
    #bid = SecureNestedField('BidSchema', only='id', required=True)
    id = fields.Integer()
    price = fields.Integer()
    work = SecureNestedField('WorkSchema', only=('id','review'), default=None)
    contractor = SecureNestedField('ContractorSchema', only='id', required=True)
    ticket_snapshot = SecureNestedField('TicketSnapshotSchema', only=('id','ticket'), required=True)

    def make_object(self, data):
        from rebase.models import WorkOffer
        return get_or_make_object(WorkOffer, data)

serializer = WorkOfferSchema(only=('id','price','work','ticket_snapshot'), skip_missing=True)
deserializer = WorkOfferSchema(only=('price','work','contractor','ticket_snapshot'), strict=True)

update_deserializer = WorkOfferSchema(only=('price',), strict=True)
update_deserializer.make_object = lambda data: data
