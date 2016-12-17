
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.views.comment import CommentSchema


class ReviewSchema(RebaseSchema):
    id = fields.Integer()
    created = fields.DateTime()
    rating = fields.Integer()
    work = SecureNestedField('WorkSchema', exclude=('review',))
    comments = SecureNestedField(CommentSchema, only=('id', 'content', 'created', 'user', 'type'), many=True, default=None)

    @post_load
    def make_review(self, data):
        from rebase.models import Review
        return self._get_or_make_object(Review, data)


serializer = ReviewSchema()
deserializer = ReviewSchema(only=('work',))
update_deserializer = ReviewSchema(only=('rating',), context={'raw': True})
