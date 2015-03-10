from marshmallow import fields, Schema

class ContractorSchema(Schema):
    id =            fields.Integer()
    user =          fields.Nested('UserSchema', only=('id', 'first_name', 'last_name'))
    busyness =      fields.Integer()
    work_offers =   fields.Nested('WorkOfferSchema', only='id', many=True)
    bank_account =  fields.Nested('BankAccountSchema', only='id')

    remote_work_history = fields.Nested('RemoteWorkHistorySchema', only='id')
    #clearances = fields.Nested('ClearanceSchema', only='id', default=None)
    #skill_sets = fields.Nested('SkillSetSchema', only='id', required=True)
    #candidates = fields.Nested('CandidateSchema', only='id', required=True)

    def make_object(self, data):
        from alveare.models import Contractor
        if data.get('id'):
            contractor = Contractor.query.get(data.get('id'))
            if not contractor:
                raise ValueError('No contractor with id {id}'.format(**data))
            return contractor
        return Contractor(**data)

serializer = ContractorSchema(skip_missing=True)
