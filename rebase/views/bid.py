from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.common.database import get_or_make_object, SecureNestedField

class BidSchema(RebaseSchema):
    id =          fields.Integer()
    auction =     SecureNestedField('AuctionSchema', only='id', required=True)
    contract =    SecureNestedField('ContractSchema', only=('id',))
    contractor =  SecureNestedField('ContractorSchema', only=('id',), required=True)
    work_offers = SecureNestedField('WorkOfferSchema', many=True, required=True)

    def make_object(self, data):
        from rebase.models import Bid
        return get_or_make_object(Bid, data)

serializer = BidSchema(only=('id', 'auction', 'contractor','work_offers'))
deserializer = BidSchema(only=('auction', 'contractor', 'work_offers'), strict=True)
update_deserializer = BidSchema(only=('id',), strict=True, skip_missing=True)
update_deserializer.make_object = lambda data: data
