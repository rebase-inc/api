from flask.ext.restful import abort
from marshmallow import fields, Schema

from alveare.models.skill_set import SkillSet
from alveare.models.contractor import Contractor
from alveare.views.contractor import ContractorSchema
from alveare.common.database import get_or_make_object

class SkillSetSchema(Schema):
    id =            fields.Integer()
    contractor =    fields.Nested(ContractorSchema,  only=('id',))

    def make_object(self, data):
        from alveare.models import SkillSet
        return get_or_make_object(SkillSet, data)

serializer = SkillSetSchema()
deserializer = SkillSetSchema(skip_missing=True)
update_deserializer = SkillSetSchema('message',)
update_deserializer.make_object = lambda data: data
