from marshmallow import fields
from alveare.common.schema import AlveareSchema

from alveare.common.database import get_or_make_object
from alveare.views.role import RoleSchema

class UserSchema(AlveareSchema):
    id = fields.Integer()
    first_name = fields.String(required=True)
    last_name = fields.String(required=True)
    email = fields.Email(required=True)
    password = fields.String(required=True)
    last_seen = fields.DateTime(required=True)
    admin = fields.Boolean(default=False)

    roles = fields.Nested('RoleSchema', only=('id','type'), many=True)


    def make_object(self, data):
        from alveare.models import User
        if tuple(data.keys()) == ('email',):
            return User.query.filter(User.email == data.get('email')).one()
        return get_or_make_object(User, data)

serializer = UserSchema(only=('id','admin','first_name','last_name','email','last_seen','roles'))

deserializer = UserSchema(only=('first_name','last_name','email','password'), strict=True)

update_deserializer = UserSchema(only=('first_name','last_name','email','password'))
update_deserializer.make_object = lambda data: data
