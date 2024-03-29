from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class BidSchema(RebaseSchema):
    id =          fields.Integer()
    auction =     SecureNestedField('AuctionSchema', only=('id', 'finish_work_by'), required=True)
    contract =    SecureNestedField('ContractSchema', exclude=('bid',))
    contractor =  SecureNestedField('ContractorSchema', only=('id', 'user'), required=True)
    work_offers = SecureNestedField('WorkOfferSchema', many=True, required=True)

    @post_load
    def make_bid(self, data):
        from rebase.models import Bid
        return self._get_or_make_object(Bid, data)


serializer = BidSchema()
deserializer = BidSchema(only=('auction', 'contractor', 'work_offers'), strict=True)
update_deserializer = BidSchema(only=('id',), context={'raw': True}, strict=True)
