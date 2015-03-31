from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object, SecureNestedField
from alveare.views.nomination import NominationSchema

class ContractorSchema(AlveareSchema):
    id =                    fields.Integer()
    busyness =              fields.Integer()
    user =                  SecureNestedField('UserSchema',              only=('id',))
    work_offers =           SecureNestedField('WorkOfferSchema',         only=('id',), many=True)
    bank_account =          SecureNestedField('BankAccountSchema',       only=('id',), default=None)
    remote_work_history =   SecureNestedField('RemoteWorkHistorySchema', only=('id',))
    skill_set =             SecureNestedField('SkillSetSchema',          only=('id',), default=None)
    clearances =            SecureNestedField('CodeClearanceSchema',     only=('id', 'project', 'pre_approved'), many=True)
    nominations =           SecureNestedField('NominationSchema',        only='id', many=True, default=None)

    def make_object(self, data):
        from alveare.models import Contractor
        return get_or_make_object(Contractor, data)

serializer =            ContractorSchema(skip_missing=True)
deserializer =          ContractorSchema(only=('user',), strict=True)
update_deserializer =   ContractorSchema(only=('id', 'busyness',))
update_deserializer.make_object = lambda data: data

