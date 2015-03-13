from marshmallow import fields, Schema
from alveare.models.skill_set import SkillSet
from alveare.models.contractor import Contractor
from alveare.views.contractor import ContractorSchema
from flask.ext.restful import abort

class SkillSetSchema(Schema):
    id =            fields.Integer()
    contractor =    fields.Nested(ContractorSchema,  only=('id', 'user'))

    def make_object(self, data):
        if data.get('id'):
            skill_set = SkillSet.query.get_or_404(data['id'])
            data.pop('id')
            for field, value in data.items():
                setattr(skill_set, field, value)
            return skill_set
        else:
            return SkillSet(data['contractor'])


deserializer =          SkillSetSchema(skip_missing=True)
update_deserializer =   SkillSetSchema()
serializer =            SkillSetSchema()
