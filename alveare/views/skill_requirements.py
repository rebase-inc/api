from marshmallow import fields, Schema
from alveare.models.skill_requirements import SkillRequirement
from flask.ext.restful import abort

class SkillRequirementSchema(Schema):
    id =            fields.Integer()

    def make_object(self, data):
        skill_requirements = SkillRequirement.query.get(data['id'])
        if skill_requirements:
            data.pop('id')
            for field, value in data:
                setattr(rwh, field, value)
            return skill_requirements
        ticket = Ticket.query.get_or_404(data['id'])
        skill_requirements = SkillRequirement(ticket)
        return skill_requirements

deserializer =          SkillRequirementSchema()
update_deserializer =   SkillRequirementSchema()
serializer =            SkillRequirementSchema()
