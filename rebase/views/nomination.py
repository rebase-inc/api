from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.models import Nomination

class NominationSchema(RebaseSchema):

    contractor_id =             fields.Integer()
    ticket_set_id =             fields.Integer()

    job_fit =    SecureNestedField('JobFitSchema',       only=('contractor_id', 'ticket_set_id', 'score'), default=None)
    contractor = SecureNestedField('ContractorSchema',   only=('id','user', 'skill_set', 'rating'), default=None)
    ticket_set = SecureNestedField('TicketSetSchema',    only=('id', 'auction'), default=None)
    auction =    SecureNestedField('AuctionSchema',      only=('id','bids'), default=None)

    @post_load
    def make_nomination(self, data):
        return get_or_make_object(Nomination, data)

deserializer =          NominationSchema()
serializer =            NominationSchema()
update_deserializer =   NominationSchema()
update_deserializer.make_object = lambda data: data
