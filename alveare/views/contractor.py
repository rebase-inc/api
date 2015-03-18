from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object

class ContractorSchema(Schema):
    id =                    fields.Integer()
    busyness =              fields.Integer()
    user =                  fields.Nested('UserSchema',         only=('id', 'first_name', 'last_name'))
    work_offers =           fields.Nested('WorkOfferSchema',    only=('id',), many=True)
    bank_account =          fields.Nested('BankAccountSchema',  only=('id',))
    remote_work_history =   fields.Nested('RemoteWorkHistorySchema',    only=('id',))
    skill_set =             fields.Nested('SkillSetSchema',             only=('id',))
    clearances =            fields.Nested('CodeClearanceSchema',        only=('id', 'project', 'pre_approved'), many=True)
    #candidates = fields.Nested('CandidateSchema', only='id', required=True)

    def make_object(self, data):
        from alveare.models import Contractor
        return get_or_make_object(Contractor, data)

# this is a hack...TODO: GET RID OF IT
@ContractorSchema.data_handler
def remove_empty_bank_account(schema, data, obj):
    if isinstance(data, list):
        return [remove_empty_bank_account(schema, elem, obj) for elem in data]
    if data.get('bank_account', None) == dict(id=0):
        data.pop('bank_account')
    return data

serializer = ContractorSchema(skip_missing=True)
deserializer = ContractorSchema(only=('user',), strict=True)
update_deserializer = ContractorSchema(only=('id', 'busyness',))
update_deserializer.make_object = lambda data: data 

