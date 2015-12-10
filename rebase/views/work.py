
from marshmallow import fields, post_load

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.views.credit import CreditSchema
from rebase.views.debit import DebitSchema
from rebase.views.mediation import MediationSchema
from rebase.views.blockage import BlockageSchema
from rebase.views.review import ReviewSchema
from rebase.views.work_offer import WorkOfferSchema


class WorkSchema(RebaseSchema):
    id =        fields.Integer()
    state =     fields.String()
    branch =    fields.String()
    clone =     fields.String()

    review =    SecureNestedField(ReviewSchema,     exclude=('work',), default=None)
    mediations = SecureNestedField(MediationSchema,  only=('id','state', 'comments'), many=True)
    blockages = SecureNestedField(BlockageSchema,  only=('id','comments'), many=True)
    debit =     SecureNestedField(DebitSchema,      only='id', default=None)
    credit =    SecureNestedField(CreditSchema,     only='id', default=None)
    offer =     SecureNestedField(WorkOfferSchema,  exclude=('work',), default=None)
    comments =  SecureNestedField('CommentSchema', only=('id', 'content', 'created', 'user', 'type'), many=True, default=None)

    @post_load
    def make_work_schema(self, data):
        from rebase.models import Work
        return self._get_or_make_object(Work, data)

class HaltEventSchema(RebaseSchema):
    comment = fields.String(required=True)

    @post_load
    def make_halt(self, data):
        return 'halt_work', data

class ReviewEventSchema(RebaseSchema):
    comment = fields.String(required=False)

    @post_load
    def make_review(self, data):
        return 'review', data

class MediateEventSchema(RebaseSchema):
    comment = fields.String(required=True)

    @post_load
    def make_mediate(self, data):
        return 'mediate', data

class CompleteEventSchema(RebaseSchema):
    comment = fields.String(required=True)
    rating = fields.Integer(required=True)

    @post_load
    def make_complete(self, data):
        return 'complete', data

class ResumeEventSchema(RebaseSchema):
    comment = fields.String(required=False)

    @post_load
    def make_resume(self, data):
        return 'resume_work', data

class FailEventSchema(RebaseSchema):

    @post_load
    def make_fail(self, data):
        return 'fail'

serializer = WorkSchema()
deserializer = WorkSchema(strict=True, only=tuple()) #TODO: Use load_only/dump_only
update_deserializer = WorkSchema(only=tuple(), context={'raw': True})

halt_event_deserializer = HaltEventSchema(strict=True)
review_event_deserializer = ReviewEventSchema()
mediate_event_deserializer = MediateEventSchema()
complete_event_deserializer = CompleteEventSchema()
resume_event_deserializer = ResumeEventSchema()
fail_event_deserializer = FailEventSchema()

