from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.common.database import get_or_make_object, SecureNestedField

class RoleSchema(AlveareSchema):
    id = fields.Integer()
    type = fields.String(required=True)

    user = SecureNestedField('UserSchema', only=('id',), required=True)

    def make_object(self, data):
        from alveare.models import Role
        return get_or_make_object(Role, data)

serializer = RoleSchema(only=('id','type','user','roles'), skip_missing=True)

deserializer = RoleSchema(only=tuple(), strict=True)

update_deserializer = RoleSchema(only=tuple())
update_deserializer.make_object = lambda data: data
