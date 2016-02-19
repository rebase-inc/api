
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class CommentSchema(RebaseSchema):
    id =        fields.Integer()
    content =   fields.String()
    created =   fields.DateTime()

    user =      SecureNestedField('UserSchema',       only=('id','name', 'photo'), required=True)
    ticket =    SecureNestedField('TicketSchema',     only=('id',), default=None)
    review =    SecureNestedField('ReviewSchema',     only=('id',), default=None)
    mediation = SecureNestedField('MediationSchema',  only=('id',), default=None)
    feedback =  SecureNestedField('FeedbackSchema',   only=('id',), default=None)

    @post_load
    def make_comment(self, data):
        from rebase.models import Comment
        return self._get_or_make_object(Comment, data)

serializer =            CommentSchema(strict=True)
deserializer =          CommentSchema(strict=True)
update_deserializer =   CommentSchema(context={'raw': True})
