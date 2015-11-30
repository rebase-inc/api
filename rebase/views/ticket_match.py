from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.utils import get_model_primary_keys
from rebase.models import TicketMatch
from rebase.views.job_fit import JobFitSchema

class TicketMatchSchema(RebaseSchema):
    skill_requirement_id =  fields.Integer()
    skill_set_id =          fields.Integer()

    skill_requirement = SecureNestedField('SkillRequirementSchema',   only=('id','skills'))
    skill_set =         SecureNestedField('SkillSetSchema',           only=('id','skills'))
    job_fit =           SecureNestedField('JobFitSchema',             only=('contractor_id', 'ticket_set_id'), default=None)

    _primary_keys = get_model_primary_keys(TicketMatch)

    @post_load
    def make_ticket_match(self, data):
        return get_or_make_object(TicketMatch, data, self._primary_keys)

serializer =            TicketMatchSchema()
deserializer =          TicketMatchSchema(strict=True)
update_deserializer =   TicketMatchSchema()
update_deserializer.make_object = lambda data: data
