from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object
from alveare.views.nomination import NominationSchema

class ContractorSchema(AlveareSchema):
    id =                    fields.Integer()
    busyness =              fields.Integer()
    user =                  fields.Nested('UserSchema',                 only=('id',))
    work_offers =           fields.Nested('WorkOfferSchema',            only=('id',), many=True)
    bank_account =          fields.Nested('BankAccountSchema',          only=('id',), default=None)
    remote_work_history =   fields.Nested('RemoteWorkHistorySchema',    only=('id',))
    skill_set =             fields.Nested('SkillSetSchema',             only=('id',), default=None)
    clearances =            fields.Nested('CodeClearanceSchema',        only=('id', 'project', 'pre_approved'), many=True)
    nominations =           fields.Nested('NominationSchema',           only='id', many=True, default=None)

    def make_object(self, data):
        from alveare.models import Contractor
        return get_or_make_object(Contractor, data)

serializer =            ContractorSchema(skip_missing=True)
deserializer =          ContractorSchema(only=('user',), strict=True)
update_deserializer =   ContractorSchema(only=('id', 'busyness',))
update_deserializer.make_object = lambda data: data

