from marshmallow import fields, Schema

class BidSchema(Schema):
    id =          fields.Integer()
    auction =     fields.Nested('AuctionSchema', only='id')
    contractor =  fields.Nested('ContractorSchema', only='id', required=True)
    work_offers = fields.Nested('WorkOfferSchema', only='id', many=True)
    #contract =   fields.Nested('ContractSchema', only='id')

    def make_object(self, data):
        from alveare.models import Bid
        if data.get('id'):
            bid = Bid.query.get(data.get('id'))
            if not bid:
                raise ValueError('No bid with id {id}'.format(**data))
            return bid
        return Bid(**data)

serializer = BidSchema(only=('id', 'auction', 'contractor','work_offers'))
deserializer = BidSchema(only=('auction', 'contractor'), strict=True)
