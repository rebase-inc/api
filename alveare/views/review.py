
from marshmallow import fields

from alveare.common.schema import AlveareSchema
from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema

#from alveare.views.work import WorkSchema

class ReviewSchema(AlveareSchema):
    id = fields.Integer()
    rating = fields.Integer(required = True)
    work = fields.Nested('WorkSchema', only='id')
    comments = fields.Nested(CommentSchema, many=True)

    def make_object(self, data):
        from alveare.models import Review, Work
        if data.get('id'):
            return Review.query.get(data['id'])
        return Review(**data)

serializer = ReviewSchema()
deserializer = ReviewSchema(only=('rating','work','comments'))

updater = ReviewSchema(only=('rating',))
updater.make_object = lambda data: data
