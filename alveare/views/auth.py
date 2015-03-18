from marshmallow import fields, Schema

class AuthSchema(Schema):
    user = fields.Nested('UserSchema', only=('id',), default=None)

serializer = AuthSchema(skip_missing=True)
deserializer = AuthSchema(strict=True)

update_deserializer = AuthSchema()
update_deserializer.make_object = lambda data: data