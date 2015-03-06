from marshmallow import fields, Schema

class UserSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    password = fields.String(load_only=True)
    last_seen = fields.DateTime(dump_only=True)

    def make_object(self, data):
        from alveare.models import User
        if data.get('id'):
            user = User.query.get(data.get('id', None))
            if not user:
                raise ValueError('No user with id {}'.format(data.get('id')))
            return user
        return User(**data)

serializer = UserSchema(only=('id','first_name','last_name','email','last_seen'))

deserializer = UserSchema(only=('first_name','last_name','email','password'))

updater = UserSchema(only=('first_name','last_name','email','password'))
updater.make_object = lambda data: data
