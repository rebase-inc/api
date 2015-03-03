from marshmallow import fields, Schema

from alveare.views import NamespacedSchema

class CommentSchema(Schema):
    id = fields.Integer()
    content = fields.String()

    def make_object(self, data):
        from alveare.models import Comment
        return Comment(**data)
