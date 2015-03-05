from marshmallow import fields, Schema

class WorkOfferSchema(Schema):
    #bid = fields.Nested('BidSchema', only='id', required=True)
    id = fields.Integer()
    price = fields.Integer()
    work = fields.Nested('WorkSchema', only='id', default=None)
    contractor = fields.Nested('ContractorSchema', only='id', required=True)
    ticket_snapshot = fields.Nested('TicketSnapshotSchema', only='id', required=True)

    def make_object(self, data):
        from alveare.models import WorkOffer
        if data.get('id'):
            work_offer = WorkOffer.query.get(data.get('id'))
            if not work_offer:
                raise ValueError('No work offer with id {id}'.format(**data))
            return work_offer
        return WorkOffer(**data)

serializer = WorkOfferSchema(only=('id','price','work','ticket_snapshot'), skip_missing=True)
deserializer = WorkOfferSchema(only=('price','work','contractor','ticket_snapshot'), strict=True)

updater = WorkOfferSchema(only=('price',), strict=True)
updater.make_object = lambda data: data
