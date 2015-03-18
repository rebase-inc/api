from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object
from alveare.common.utils import primary_key
from alveare.models import Candidate

class CandidateSchema(Schema):

    contractor_id =             fields.Integer()
    ticket_set_id =             fields.Integer()
    approved_for_auction_id =   fields.Integer()

    job_fit =                   fields.Nested('JobFitSchema',       only=('contractor_id', 'ticket_set_id'), default=None)
    contractor =                fields.Nested('ContractorSchema',   only=('id',), default=None)
    ticket_set =                fields.Nested('TicketSetSchema',    only=('id',), default=None)

    _primary_keys = primary_key(Candidate)

    def make_object(self, data):
        return get_or_make_object(Candidate, data, self._primary_keys)

deserializer =          CandidateSchema(skip_missing=True)
serializer =            CandidateSchema(skip_missing=True)
update_deserializer =   CandidateSchema()
update_deserializer.make_object = lambda data: data
