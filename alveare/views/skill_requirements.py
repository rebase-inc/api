from marshmallow import fields, Schema
from alveare.models.skill_requirements import SkillRequirements
from flask.ext.restful import abort

class SkillRequirementsSchema(Schema):
    id =            fields.Integer()

    def make_object(self, data):
        skill_requirements = SkillRequirements.query.get(data['id'])
        if skill_requirements:
            data.pop('id')
            for field, value in data:
                setattr(rwh, field, value)
            return skill_requirements
        ticket = Ticket.query.get_or_404(data['id'])
        skill_requirements = SkillRequirements(ticket)
        return skill_requirements

deserializer =          SkillRequirementsSchema()
update_deserializer =   SkillRequirementsSchema()
serializer =            SkillRequirementsSchema()
