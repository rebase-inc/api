from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views.review import ReviewSchema
from alveare.views.mediation import MediationSchema
from alveare.views.debit import DebitSchema
from alveare.views.credit import CreditSchema
from alveare.views.work_offer import WorkOfferSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class WorkSchema(AlveareSchema):
    id = fields.Integer()
    state = fields.String()
    review = SecureNestedField(ReviewSchema, exclude=('work',), default=None)
    mediation = SecureNestedField(MediationSchema, only=('id','state'), attribute='mediation_rounds', many=True)
    debit = SecureNestedField(DebitSchema, only='id', default=None)
    credit = SecureNestedField(CreditSchema, only='id', default=None)
    offer = SecureNestedField(WorkOfferSchema, only='id', default=None)

    def make_object(self, data):
        from alveare.models import Work
        return get_or_make_object(Work, data)

serializer = WorkSchema(only=('id','state','mediation','review','debit','credit','offer'), skip_missing=True)
deserializer = WorkSchema(only=tuple())
update_deserializer = WorkSchema(only=tuple())
update_deserializer.make_object = lambda data: data
