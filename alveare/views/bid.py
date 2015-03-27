from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.common.database import get_or_make_object

class BidSchema(AlveareSchema):
    id =          fields.Integer()
    auction =     fields.Nested('AuctionSchema', only='id')
    contractor =  fields.Nested('ContractorSchema', only='id', required=True)
    work_offers = fields.Nested('WorkOfferSchema', only='id', many=True)
    #contract =   fields.Nested('ContractSchema', only='id')

    def make_object(self, data):
        from alveare.models import Bid
        return get_or_make_object(Bid, data)

serializer = BidSchema(only=('id', 'auction', 'contractor','work_offers'))
deserializer = BidSchema(only=('auction', 'contractor'), strict=True)
update_deserializer = BidSchema(only=tuple(), strict=True)
update_deserializer.make_object = lambda data: data
