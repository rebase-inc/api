from marshmallow import fields, Schema
#from .organization import Organization

class Project(Schema):
    id = fields.Integer()
    name = fields.String()
    #organization = fields.Nested(Organization)

serializer = Project(only=('id','first_name','last_name','last_seen'))
deserializer = Project(only=('first_name','last_name','last_seen'))

