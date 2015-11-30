from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import SecureNestedField

class AuthSchema(RebaseSchema):
    user = SecureNestedField('UserSchema', only=('id', 'email',), required=True)
    password = fields.String(required=True)

serializer = AuthSchema()
deserializer = AuthSchema(strict=True)

update_deserializer = AuthSchema()
#update_deserializer.make_object = lambda data: data
