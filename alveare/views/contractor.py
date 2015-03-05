from marshmallow import fields, Schema

class ContractorSchema(Schema):
    id = fields.Integer()
    busyness = fields.Integer()
    #clearances = fields.Nested('ClearanceSchema', only='id', default=None)
    #skill_sets = fields.Nested('SkillSetSchema', only='id', required=True)
    #remote_work_history = fields.Nested('RemoteWorkHistorySchema', only='id')
    #candidates = fields.Nested('CandidateSchema', only='id', required=True)
    work_offers = fields.Nested('WorkOfferSchema', only='id', many=True)

    def make_object(self, data):
        from alveare.models import Contractor
        if data.get('id'):
            contractor = Contractor.query.get(data.get('id'))
            if not contractor:
                raise ValueError('No contractor with id {id}'.format(**data))
            return contractor
        return Contractor(**data)

serializer = ContractorSchema(only=('id','busyness','work_offers'), skip_missing=True)
#deserializer = WorkOfferSchema(only=('price','work','contractor','ticket_snapshot'), strict=True)
