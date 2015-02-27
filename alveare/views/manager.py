from marshmallow import fields, Schema

class Manager(Schema):
    id =                fields.Integer()
    organization_id =   fields.Integer()

deserializer = serializer = Manager()
