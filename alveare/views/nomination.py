from marshmallow import fields, Schema
from alveare.common.database import get_or_make_object
from alveare.common.utils import primary_key
from alveare.models import Nomination

class NominationSchema(Schema):

    contractor_id =             fields.Integer()
    ticket_set_id =             fields.Integer()
    approved_for_auction_id =   fields.Integer()

    job_fit =                   fields.Nested('JobFitSchema', only=('contractor_id', 'ticket_set_id'))

    _primary_keys = primary_key(Nomination)

    def make_object(self, data):
        return get_or_make_object(Nomination, data, self._primary_keys)

deserializer =          NominationSchema(skip_missing=True)
serializer =            NominationSchema()
update_deserializer =   NominationSchema()
update_deserializer.make_object = lambda data: data
