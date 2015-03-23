from marshmallow import fields
from alveare.common.schema import AlveareSchema

class AuthSchema(AlveareSchema):
    user = fields.Nested('UserSchema', only=('id',), default=None)

serializer = AuthSchema(skip_missing=True)
deserializer = AuthSchema(strict=True)

update_deserializer = AuthSchema()
update_deserializer.make_object = lambda data: data
