
from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema
from rebase.common.database import SecureNestedField

class BlockageSchema(RebaseSchema):
    id =            fields.Integer()
    created =       fields.DateTime()
    ended =         fields.DateTime()
    comments =      SecureNestedField('CommentSchema', only=('id', 'content', 'created', 'user', 'type'), many=True, default=None)

    @post_load
    def make_blockage(self, data):
        from rebase.models import Blockage
        return self._get_or_make_object(Blockage, data)


serializer =            BlockageSchema()
deserializer =          BlockageSchema(strict=True)
update_deserializer =   BlockageSchema(only=('id', ), context={'raw': True})
