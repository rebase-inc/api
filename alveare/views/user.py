from marshmallow import fields, Schema

from alveare.common.database import get_or_make_object

class UserSchema(Schema):
    id = fields.Integer()
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    last_seen = fields.DateTime(required=True)

    def make_object(self, data):
        from alveare.models import User
        return get_or_make_object(User, data)

serializer = UserSchema(only=('id','first_name','last_name','email','last_seen'))

deserializer = UserSchema(only=('first_name','last_name','email','password'), strict=True)

update_deserializer = UserSchema(only=('first_name','last_name','email','password'))
update_deserializer.make_object = lambda data: data
