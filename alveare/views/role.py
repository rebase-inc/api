from marshmallow import fields, Schema

from alveare.common.database import get_or_make_object

class RoleSchema(Schema):
    id = fields.Integer()
    type = fields.String(required=True)

    user = fields.Nested('UserSchema', only=('id',), required=True)

    def make_object(self, data):
        from alveare.models import Role
        return get_or_make_object(Role, data)

serializer = RoleSchema(only=('id','type','user','roles'), skip_missing=True)

deserializer = RoleSchema(only=tuple(), strict=True)

update_deserializer = RoleSchema(only=tuple())
update_deserializer.make_object = lambda data: data
