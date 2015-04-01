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

class HaltEventSchema(AlveareSchema):
    reason = fields.String(required=True)
    def make_object(self, data):
        return 'halt_work', data.pop('reason')

class ReviewEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'review'

class MediateEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'mediate'

class CompleteEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'complete'

class ResumeEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'resume_work'

class FailEventSchema(AlveareSchema):
    def make_object(self, data):
        return 'fail'

serializer = WorkSchema(only=('id','state','mediation','review','debit','credit','offer'), skip_missing=True)
deserializer = WorkSchema(only=tuple())
update_deserializer = WorkSchema(only=tuple())
update_deserializer.make_object = lambda data: data

halt_event_deserializer = HaltEventSchema(strict=True)
review_event_deserializer = ReviewEventSchema()
mediate_event_deserializer = MediateEventSchema()
complete_event_deserializer = CompleteEventSchema()
resume_event_deserializer = ResumeEventSchema()
fail_event_deserializer = FailEventSchema()

