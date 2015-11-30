from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class WorkOfferSchema(RebaseSchema):
    #bid = SecureNestedField('BidSchema', only='id', required=True)
    id = fields.Integer()
    price = fields.Integer()
    work = SecureNestedField('WorkSchema', only=('id','review', 'state', 'mediations', 'clone'), default=None)
    contractor = SecureNestedField('ContractorSchema', only=('id', 'user'))
    bid = SecureNestedField('BidSchema', exclude=('work_offers',))
    ticket_snapshot = SecureNestedField('TicketSnapshotSchema', only=('id','ticket'))

    def make_object(self, data):
        from rebase.models import WorkOffer
        return get_or_make_object(WorkOffer, data)

serializer = WorkOfferSchema(only=('id', 'price', 'work', 'contractor', 'ticket_snapshot'))
deserializer = WorkOfferSchema(only=('id', 'price','contractor','ticket_snapshot'), strict=True)

update_deserializer = WorkOfferSchema(strict=True)
update_deserializer.make_object = lambda data: data
