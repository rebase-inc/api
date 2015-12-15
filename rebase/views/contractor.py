from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.views.nomination import NominationSchema

class ContractorSchema(RebaseSchema):
    id =                    fields.Integer()
    type =                  fields.String()
    busyness =              fields.Integer()
    rating =                fields.Integer()
    user =                  SecureNestedField('UserSchema',              only=('id', 'name', 'photo'))
    work_offers =           SecureNestedField('WorkOfferSchema',         only=('id',), many=True)
    bank_account =          SecureNestedField('BankAccountSchema',       only=('id',), default=None)
    remote_work_history =   SecureNestedField('RemoteWorkHistorySchema', only=('id',))
    skill_set =             SecureNestedField('SkillSetSchema',          only=('id','skills'), default=None)
    clearances =            SecureNestedField('CodeClearanceSchema',     only=('id', 'project', 'pre_approved'), many=True)
    nominations =           SecureNestedField('NominationSchema',        only='id', many=True, default=None)

    @post_load
    def make_contractor(self, data):
        from rebase.models import Contractor
        return self._get_or_make_object(Contractor, data)

serializer =            ContractorSchema()
deserializer =          ContractorSchema(only=('user',), strict=True)
update_deserializer =   ContractorSchema(only=('busyness',), context={'raw': True})
