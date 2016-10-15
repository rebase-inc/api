from logging import getLogger

from flask.ext.restful import abort
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.skill_set import SkillSet
from rebase.models.contractor import Contractor
from rebase.views.contractor import ContractorSchema


logger = getLogger()


class SkillsField(fields.Field):

    def __init__(self, key_field, nested_field, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
        #logger.debug('in DictField._serializer, value: %s', value)
        if value is not None:
            return tuple(
                (key, val) for key, val in value.items()
            )
        return tuple(('FOO', 'BAR'))


class SkillSetSchema(RebaseSchema):
    id =            fields.Integer()
    skills =        SkillsField(fields.Str(), fields.Float(), default={})
    contractor =    SecureNestedField(ContractorSchema,  only=('id',))

    @post_load
    def make_skill_set(self, data):
        from rebase.models import SkillSet
        return self._get_or_make_object(SkillSet, data)

serializer = SkillSetSchema()
deserializer = SkillSetSchema()
update_deserializer = SkillSetSchema('message', context={'raw': True}) # TODO: Figure out what the message parameter is for
