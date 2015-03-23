from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views import NamespacedSchema

class CommentSchema(AlveareSchema):
    id =        fields.Integer()
    content =   fields.String()

    def make_object(self, data):
        from alveare.models import Comment
        return Comment(**data)
