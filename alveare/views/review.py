
from marshmallow import fields, Schema

from alveare.views import NamespacedSchema
from alveare.views.comment import CommentSchema

class ReviewSchema(Schema):
    id = fields.Integer()
    rating = fields.Integer()
    work = fields.Nested('WorkSchema', only='id')
    comments = fields.Nested(CommentSchema, many=True)

    def make_object(self, data):
        from alveare.models import Review
        return Review(**data)

#serializer = WorkSchema(only=('id','state','review','mediation'))

#deserializer = UserSchema(only=('first_name','last_name','email','password'))

#updater = UserSchema(only=('first_name','last_name','email','password'))
#updater.make_object = lambda data: data
