from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.views import NamespacedSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class CommentSchema(AlveareSchema):
    id =        fields.Integer()
    content =   fields.String()

    ticket =    SecureNestedField('TicketSchema',     only=('id',), default=None)
    review =    SecureNestedField('ReviewSchema',     only=('id',), default=None)
    mediation = SecureNestedField('MediationSchema',  only=('id',), default=None)
    feedback =  SecureNestedField('FeedbackSchema',   only=('id',), default=None)

    def make_object(self, data):
        from alveare.models import Comment
        return get_or_make_object(Comment, data)

serializer =            CommentSchema(skip_missing=True)
deserializer =          CommentSchema(strict=True)
update_deserializer =   CommentSchema()
update_deserializer.make_object = lambda data: data
