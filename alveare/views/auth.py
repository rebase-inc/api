from marshmallow import fields, Schema

class AuthSchema(Schema):
    user = fields.Nested('UserSchema', only=('id',), required=True)
    password = fields.String(required=True)

serializer = AuthSchema(skip_missing=True)
deserializer = AuthSchema(strict=True)

update_deserializer = AuthSchema()
update_deserializer.make_object = lambda data: data
