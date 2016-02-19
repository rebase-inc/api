from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models import TicketMatch
from rebase.views.job_fit import JobFitSchema


class TicketMatchSchema(RebaseSchema):
    skill_requirement_id =  fields.Integer()
    skill_set_id =          fields.Integer()

    skill_requirement = SecureNestedField('SkillRequirementSchema',   only=('id','skills'))
    skill_set =         SecureNestedField('SkillSetSchema',           only=('id','skills'))
    job_fit =           SecureNestedField('JobFitSchema',             only=('contractor_id', 'ticket_set_id'), default=None)

    @post_load
    def make_ticket_match(self, data):
        return self._get_or_make_object(TicketMatch, data)


serializer =            TicketMatchSchema()
deserializer =          TicketMatchSchema(strict=True)
update_deserializer =   TicketMatchSchema(context={'raw': True})
