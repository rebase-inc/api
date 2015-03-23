from flask.ext.restful import abort
from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.models.skill_requirement import SkillRequirement
from alveare.common.database import get_or_make_object

class SkillRequirementSchema(AlveareSchema):
    id =            fields.Integer()

    def make_object(self, data):
        from alveare.models import SkillRequirement
        return get_or_make_object(SkillRequirement, data)

serializer =            SkillRequirementSchema()
deserializer =          SkillRequirementSchema()
update_deserializer = SkillRequirementSchema('message',)
update_deserializer.make_object = lambda data: data 

