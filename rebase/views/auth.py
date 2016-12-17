from marshmallow import fields

from rebase.common.schema import RebaseSchema, SecureNestedField


class AuthSchema(RebaseSchema):
    user = SecureNestedField('UserSchema', only=('id', 'email',), required=True)
    password = fields.String(required=True)


serializer = AuthSchema()
deserializer = AuthSchema(strict=True)
update_deserializer = None
