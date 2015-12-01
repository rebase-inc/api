from flask.ext.restful import abort
from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema

from rebase.models.skill_set import SkillSet
from rebase.models.contractor import Contractor
from rebase.views.contractor import ContractorSchema
from rebase.common.database import get_or_make_object, SecureNestedField

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

class SkillSetSchema(RebaseSchema):
    id =            fields.Integer()
    skills =        DictField(fields.Str(), fields.Float(), default={})
    contractor =    SecureNestedField(ContractorSchema,  only=('id',))

    @post_load
    def make_skill_set(self, data):
        from rebase.models import SkillSet
        return self._get_or_make_object(SkillSet, data)

serializer = SkillSetSchema()
deserializer = SkillSetSchema()
update_deserializer = SkillSetSchema('message', context={'raw': True}) # TODO: Figure out what the message parameter is for
