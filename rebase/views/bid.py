from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.common.database import get_or_make_object, SecureNestedField

class BidSchema(RebaseSchema):
    id =          fields.Integer()
    auction =     SecureNestedField('AuctionSchema', only=('id', 'finish_work_by'), required=True)
    contract =    SecureNestedField('ContractSchema', exclude=('bid',))
    contractor =  SecureNestedField('ContractorSchema', only=('id', 'user'), required=True)
    work_offers = SecureNestedField('WorkOfferSchema', many=True, required=True)

    def make_object(self, data):
        from rebase.models import Bid
        return get_or_make_object(Bid, data)

serializer = BidSchema()
deserializer = BidSchema(only=('auction', 'contractor', 'work_offers'), strict=True)
update_deserializer = BidSchema(only=('id',), strict=True)
update_deserializer.make_object = lambda data: data
