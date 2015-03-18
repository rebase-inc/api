from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object
from alveare.common.utils import primary_key
from alveare.models import TicketMatch
from alveare.views.job_fit import JobFitSchema

class TicketMatchSchema(Schema):
    skill_requirement_id =  fields.Integer()
    skill_set_id =          fields.Integer()
    score =                 fields.Integer()

    skill_requirement = fields.Nested('SkillRequirementSchema',   only=('id',))
    skill_set =         fields.Nested('SkillSetSchema',           only=('id',))
    job_fit =           fields.Nested('JobFitSchema',             only=('contractor_id', 'ticket_set_id'), required=False, default=None)

    _primary_keys = primary_key(TicketMatch)

    def make_object(self, data):
        return get_or_make_object(TicketMatch, data, self._primary_keys)

deserializer =          TicketMatchSchema(skip_missing=True)
serializer =            TicketMatchSchema()
update_deserializer =   TicketMatchSchema(only=('score',))
update_deserializer.make_object = lambda data: data
