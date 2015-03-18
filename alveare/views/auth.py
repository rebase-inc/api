from marshmallow import fields, Schema

from alveare.common.database import get_or_make_object, update_object

class AuthSchema(Schema):
    user = fields.Nested('UserSchema', only=('id',), required=True)

serializer = AuthSchema()
deserializer = AuthSchema(strict=True)

update_deserializer = AuthSchema()
update_deserializer.make_object = lambda data: data
