
from marshmallow import fields

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.views.credit import CreditSchema
from rebase.views.debit import DebitSchema
from rebase.views.mediation import MediationSchema
from rebase.views.review import ReviewSchema
from rebase.views.work_offer import WorkOfferSchema


class WorkSchema(RebaseSchema):
    id =        fields.Integer()
    state =     fields.String()
    branch =    fields.String()
    clone =     fields.String()

    review =    SecureNestedField(ReviewSchema,     exclude=('work',), default=None)
    mediations = SecureNestedField(MediationSchema,  only=('id','state'), many=True)
    debit =     SecureNestedField(DebitSchema,      only='id', default=None)
    credit =    SecureNestedField(CreditSchema,     only='id', default=None)
    offer =     SecureNestedField(WorkOfferSchema,  exclude=('work',), default=None)

    def make_object(self, data):
        from rebase.models import Work
        return get_or_make_object(Work, data)


class HaltEventSchema(RebaseSchema):
    reason = fields.String(required=True)
    def make_object(self, data):
        return 'halt_work', data.pop('reason')

class ReviewEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'review'

class MediateEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'mediate'

class CompleteEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'complete'

class ResumeEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'resume_work'

class FailEventSchema(RebaseSchema):
    def make_object(self, data):
        return 'fail'

serializer = WorkSchema(skip_missing=True)
deserializer = WorkSchema(only=tuple())
update_deserializer = WorkSchema(only=tuple())
update_deserializer.make_object = lambda data: data

halt_event_deserializer = HaltEventSchema(strict=True)
review_event_deserializer = ReviewEventSchema()
mediate_event_deserializer = MediateEventSchema()
complete_event_deserializer = CompleteEventSchema()
resume_event_deserializer = ResumeEventSchema()
fail_event_deserializer = FailEventSchema()

