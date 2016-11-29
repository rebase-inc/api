from flask_restful import abort
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.skill_requirement import SkillRequirement
from rebase.views.ticket import TicketSchema


class DictField(fields.Field):

    def __init__(self, key_field, nested_field, *args, **kwargs):
        fields.Field.__init__(self, *args, **kwargs)
        self.key_field = key_field
        self.nested_field = nested_field

    def _deserialize(self, value):
        ret = {}
        if value:
            for key, val in value.items():
                k = self.key_field.deserialize(key)
                v = self.nested_field.deserialize(val)
                ret[k] = v
        return ret

    def _serialize(self, value, attr, obj):
        ret = {}
        if value:
            for key, val in value.items():
                k = self.key_field._serialize(key, attr, obj)
                v = self.nested_field.serialize(key, self.get_value(attr, obj))
                ret[k] = v
        return ret

class SkillRequirementSchema(RebaseSchema):
    id =        fields.Integer()
    skills =    DictField(fields.Str(), fields.Float(), default={})
    ticket =    SecureNestedField(TicketSchema,  only=('id',))

    @post_load
    def make_skill_requirement(self, data):
        from rebase.models import SkillRequirement
        return self._get_or_make_object(SkillRequirement, data)

serializer =            SkillRequirementSchema()
deserializer =          SkillRequirementSchema()
update_deserializer = SkillRequirementSchema('message', context={'raw': True})

