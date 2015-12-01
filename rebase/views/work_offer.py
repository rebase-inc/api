from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.models import WorkOffer

class WorkOfferSchema(RebaseSchema):

    class Meta:
        dump_only = ('work',)

    model = WorkOffer

    id = fields.Integer()
    price = fields.Integer()
    work = SecureNestedField('WorkSchema', only=('id','review', 'state', 'mediations', 'clone'), default=None)
    contractor = SecureNestedField('ContractorSchema', only=('id', 'user'))
    bid = SecureNestedField('BidSchema', exclude=('work_offers',))
    ticket_snapshot = SecureNestedField('TicketSnapshotSchema', only=('id','ticket'))

    @post_load
    def make_work_offer(self, data):
        return self._get_or_make_object(data)

serializer = WorkOfferSchema()
deserializer = WorkOfferSchema(strict=True)
update_deserializer = WorkOfferSchema(context={'raw': True})
