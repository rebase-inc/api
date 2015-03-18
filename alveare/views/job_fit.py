from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object
from alveare.common.utils import primary_key
from alveare.models import JobFit
from alveare.views.nomination import NominationSchema

class JobFitSchema(Schema):

    contractor_id =  fields.Integer()
    ticket_set_id =  fields.Integer()
    score =          fields.Integer()

    ticket_matches = fields.Nested('TicketMatchSchema', only=('skill_requirement_id',   'skill_set_id'), many=True)
    nomination =     fields.Nested('NominationSchema',  only=('contractor_id',          'ticket_set_id'))

    _primary_keys = primary_key(JobFit)

    def make_object(self, data):
        return get_or_make_object(JobFit, data, self._primary_keys)

deserializer =          JobFitSchema(skip_missing=True)
serializer =            JobFitSchema()
update_deserializer =   JobFitSchema(only=('score',))
update_deserializer.make_object = lambda data: data
