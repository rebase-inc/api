from marshmallow import fields
from rebase.common.schema import AlveareSchema
from rebase.common.database import SecureNestedField

class AuthSchema(AlveareSchema):
    user = SecureNestedField('UserSchema', only=('id', 'email',), required=True)
    password = fields.String(required=True)

serializer = AuthSchema(skip_missing=True)
deserializer = AuthSchema(strict=True)

update_deserializer = AuthSchema()
update_deserializer.make_object = lambda data: data
