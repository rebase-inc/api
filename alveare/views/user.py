from marshmallow import fields, Schema

class User(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    email = fields.Email()
    hashed_password = fields.String()
    last_seen = fields.DateTime()

serializer = User(only=('id','first_name','last_name','last_seen'))
deserializer = User(only=('first_name','last_name','last_seen'))

