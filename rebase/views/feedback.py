from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class FeedbackSchema(RebaseSchema):
    id =            fields.Integer()
    auction =       SecureNestedField('AuctionSchema', only=('id',))
    contractor =    SecureNestedField('ContractorSchema', only=('id',), required=True)
    comment =       SecureNestedField('CommentSchema', only=('id', 'content', 'created', 'user', 'type'), required=False)

    @post_load
    def make_feedback(self, data):
        from rebase.models import Feedback
        return self._get_or_make_object(Feedback, data)


serializer = FeedbackSchema()
deserializer = FeedbackSchema(strict=True)
update_deserializer = FeedbackSchema(context={'raw': True})
