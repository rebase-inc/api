from marshmallow import fields, Schema
#from alveare.views.skill_requirement import SkillRequirementSchema
from alveare.common.resource import get_or_make_object, update_object, primary_key
from alveare.models import TicketMatch

class TicketMatchSchema(Schema):
    skill_requirement_id =  fields.Integer()
    skill_set_id =          fields.Integer()
    score =                 fields.Integer()

    skill_requirement = fields.Nested('SkillRequirementSchema',   only=('id',))
    skill_set =         fields.Nested('SkillSetSchema',           only=('id',))
    #job_fit =           fields.Nested('JobFitSchema',             only=('id',))

    ids = primary_key(TicketMatch)

    def make_object(self, data):
        return get_or_make_object(TicketMatch, data, self.ids)

    def _update_object(self, data):
        return update_object(TicketMatch, data, self.ids)

deserializer =          TicketMatchSchema(skip_missing=True)
serializer =            TicketMatchSchema()
update_deserializer =   TicketMatchSchema()
update_deserializer.make_object = update_deserializer._update_object
