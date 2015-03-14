from flask.ext.restful import abort
from marshmallow import fields, Schema

from alveare.models.skill_requirement import SkillRequirement
from alveare.common.resource import get_or_make_object, update_object

class SkillRequirementSchema(Schema):
    id =            fields.Integer()

    def make_object(self, data):
        from alveare.models import SkillRequirement
        return get_or_make_object(SkillRequirement, data)

    def _update_object(self, data):
        from alveare.models import SkillRequirement
        return update_object(SkillRequirement, data)

serializer =            SkillRequirementSchema()
deserializer =          SkillRequirementSchema()
update_deserializer = SkillRequirementSchema('message',)
update_deserializer.make_object = update_deserializer._update_object

