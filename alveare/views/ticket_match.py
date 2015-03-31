from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object, SecureNestedField
from alveare.common.utils import get_model_primary_keys
from alveare.models import TicketMatch
from alveare.views.job_fit import JobFitSchema

class TicketMatchSchema(AlveareSchema):
    skill_requirement_id =  fields.Integer()
    skill_set_id =          fields.Integer()
    score =                 fields.Integer()

    skill_requirement = SecureNestedField('SkillRequirementSchema',   only=('id',))
    skill_set =         SecureNestedField('SkillSetSchema',           only=('id',))
    job_fit =           SecureNestedField('JobFitSchema',             only=('contractor_id', 'ticket_set_id'), required=False, default=None)

    _primary_keys = get_model_primary_keys(TicketMatch)

    def make_object(self, data):
        return get_or_make_object(TicketMatch, data, self._primary_keys)

serializer =            TicketMatchSchema()
deserializer =          TicketMatchSchema(skip_missing=True)
update_deserializer =   TicketMatchSchema(only=('score',))
update_deserializer.make_object = lambda data: data
