from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import get_or_make_object, SecureNestedField
from alveare.common.utils import get_model_primary_keys
from alveare.models import Nomination

class NominationSchema(AlveareSchema):

    contractor_id =             fields.Integer()
    ticket_set_id =             fields.Integer()

    job_fit =    SecureNestedField('JobFitSchema',       only=('contractor_id', 'ticket_set_id'), default=None)
    contractor = SecureNestedField('ContractorSchema',   only=('id',), default=None)
    ticket_set = SecureNestedField('TicketSetSchema',    only=('id',), default=None)
    auction =    SecureNestedField('AuctionSchema',    only=('id',), default=None)

    _primary_keys = get_model_primary_keys(Nomination)

    def make_object(self, data):
        return get_or_make_object(Nomination, data, self._primary_keys)

deserializer =          NominationSchema(skip_missing=True)
serializer =            NominationSchema(skip_missing=True)
update_deserializer =   NominationSchema()
update_deserializer.make_object = lambda data: data
