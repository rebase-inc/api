from marshmallow import fields

from rebase.common.schema import RebaseSchema, SecureNestedField


class PhotoSchema(RebaseSchema):
    id =  fields.Integer()
    url = fields.String(required=True)

serializer = PhotoSchema(only='url')
