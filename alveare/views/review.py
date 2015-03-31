
from marshmallow import fields

from alveare.common.schema import AlveareSchema
from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class ReviewSchema(AlveareSchema):
    id = fields.Integer()
    rating = fields.Integer(required = True)
    work = SecureNestedField('WorkSchema', only='id')
    comments = SecureNestedField(CommentSchema, many=True)

    def make_object(self, data):
        from alveare.models import Review
        return get_or_make_object(Review, data)

serializer = ReviewSchema()
deserializer = ReviewSchema(only=('rating','work','comments'))

update_deserializer = ReviewSchema(only=('rating',))
update_deserializer.make_object = lambda data: data
