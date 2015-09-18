from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.common.database import get_or_make_object, SecureNestedField

class PhotoSchema(RebaseSchema):
    id =  fields.Integer()
    url = fields.String(required=True)

serializer = PhotoSchema(only='url')
