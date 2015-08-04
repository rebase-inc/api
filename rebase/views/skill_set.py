from flask.ext.restful import abort
from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.models.skill_set import SkillSet
from rebase.models.contractor import Contractor
from rebase.views.contractor import ContractorSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class SkillSetSchema(RebaseSchema):
    id =            fields.Integer()
    contractor =    SecureNestedField(ContractorSchema,  only=('id',))

    def make_object(self, data):
        from rebase.models import SkillSet
        return get_or_make_object(SkillSet, data)

serializer = SkillSetSchema()
deserializer = SkillSetSchema(skip_missing=True)
update_deserializer = SkillSetSchema('message',)
update_deserializer.make_object = lambda data: data
