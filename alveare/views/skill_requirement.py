from marshmallow import fields, Schema
from alveare.models.skill_requirement import SkillRequirement
from flask.ext.restful import abort

class SkillRequirementSchema(Schema):
    id =            fields.Integer()

    def make_object(self, data):
        skill_requirement = SkillRequirement.query.get(data['id'])
        if skill_requirement:
            data.pop('id')
            for field, value in data:
                setattr(rwh, field, value)
            return skill_requirement
        ticket = Ticket.query.get_or_404(data['id'])
        skill_requirement = SkillRequirement(ticket)
        return skill_requirement

deserializer =          SkillRequirementSchema()
update_deserializer =   SkillRequirementSchema()
serializer =            SkillRequirementSchema()
