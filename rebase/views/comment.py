from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.views import NamespacedSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class CommentSchema(RebaseSchema):
    id =        fields.Integer()
    content =   fields.String()
    created =   fields.DateTime()

    user =      SecureNestedField('UserSchema',       only=('id','first_name', 'last_name', 'photo'), default=None)
    ticket =    SecureNestedField('TicketSchema',     only=('id',), default=None)
    review =    SecureNestedField('ReviewSchema',     only=('id',), default=None)
    mediation = SecureNestedField('MediationSchema',  only=('id',), default=None)
    feedback =  SecureNestedField('FeedbackSchema',   only=('id',), default=None)

    def make_object(self, data):
        from rebase.models import Comment
        return get_or_make_object(Comment, data)

serializer =            CommentSchema(skip_missing=True)
deserializer =          CommentSchema(strict=True)
update_deserializer =   CommentSchema()
update_deserializer.make_object = lambda data: data
