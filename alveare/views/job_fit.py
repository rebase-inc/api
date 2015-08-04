from marshmallow import fields
from rebase.common.schema import AlveareSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.utils import get_model_primary_keys
from rebase.models import JobFit
from rebase.views.nomination import NominationSchema

class JobFitSchema(AlveareSchema):

    contractor_id =  fields.Integer()
    ticket_set_id =  fields.Integer()
    score =          fields.Integer()

    ticket_matches = SecureNestedField('TicketMatchSchema', only=('skill_requirement_id',   'skill_set_id'), many=True)
    nomination =     SecureNestedField('NominationSchema',  only=('contractor_id',          'ticket_set_id'))

    _primary_keys = get_model_primary_keys(JobFit)

    def make_object(self, data):
        return get_or_make_object(JobFit, data, self._primary_keys)

deserializer =          JobFitSchema(skip_missing=True)
serializer =            JobFitSchema()
update_deserializer =   JobFitSchema(only=('score',))
update_deserializer.make_object = lambda data: data
