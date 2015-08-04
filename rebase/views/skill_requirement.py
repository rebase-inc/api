from flask.ext.restful import abort
from marshmallow import fields

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.skill_requirement import SkillRequirement
from rebase.views.ticket import TicketSchema

class SkillRequirementSchema(RebaseSchema):
    id =        fields.Integer()
    ticket =    SecureNestedField(TicketSchema,  only=('id',))

    def make_object(self, data):
        from rebase.models import SkillRequirement
        return get_or_make_object(SkillRequirement, data)

serializer =            SkillRequirementSchema()
deserializer =          SkillRequirementSchema()
update_deserializer = SkillRequirementSchema('message',)
update_deserializer.make_object = lambda data: data 

