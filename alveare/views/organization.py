from marshmallow import fields, Schema
#from .project import Project

class Organization(Schema):
    id = fields.Integer()
    name = fields.String()
    #projects = fields.Nested(Project, many=True)

serializer = Organization(only=('id','name'))
deserializer = Organization(only=('name'))

