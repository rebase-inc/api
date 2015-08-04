
from marshmallow import fields

from rebase.common.schema import RebaseSchema
from rebase.views import NamespacedSchema
from rebase.views.comment import CommentSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class ReviewSchema(RebaseSchema):
    id = fields.Integer()
    rating = fields.Integer(required = True)
    work = SecureNestedField('WorkSchema', only='id')
    comments = SecureNestedField(CommentSchema, only=('id',), many=True, default=None)

    def make_object(self, data):
        from rebase.models import Review
        return get_or_make_object(Review, data)

serializer = ReviewSchema()
deserializer = ReviewSchema(only=('rating','work','comments'))

update_deserializer = ReviewSchema(only=('rating',))
update_deserializer.make_object = lambda data: data
