from marshmallow import fields, Schema

class User(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    password = fields.String()
    last_seen = fields.DateTime()

    def make_object(self, data):
        from alveare.models import User
        return User(**data)

serializer = User(only=('id','first_name','last_name','email','last_seen'))
deserializer = User(only=('first_name','last_name','email','password'))

