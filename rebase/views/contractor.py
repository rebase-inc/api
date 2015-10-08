from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.views.nomination import NominationSchema

class ContractorSchema(RebaseSchema):
    id =                    fields.Integer()
    busyness =              fields.Integer()
    rating =                fields.Integer()
    user =                  SecureNestedField('UserSchema',              only=('id', 'first_name', 'last_name'))
    work_offers =           SecureNestedField('WorkOfferSchema',         only=('id',), many=True)
    bank_account =          SecureNestedField('BankAccountSchema',       only=('id',), default=None)
    remote_work_history =   SecureNestedField('RemoteWorkHistorySchema', only=('id',))
    skill_set =             SecureNestedField('SkillSetSchema',          only=('id','skills'), default=None)
    clearances =            SecureNestedField('CodeClearanceSchema',     only=('id', 'project', 'pre_approved'), many=True)
    nominations =           SecureNestedField('NominationSchema',        only='id', many=True, default=None)

    def make_object(self, data):
        from rebase.models import Contractor
        return get_or_make_object(Contractor, data)

serializer =            ContractorSchema(skip_missing=True)
deserializer =          ContractorSchema(only=('user',), strict=True)
update_deserializer =   ContractorSchema(only=('busyness',))
update_deserializer.make_object = lambda data: data

