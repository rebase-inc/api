from marshmallow import fields, Schema
#from .project import Project

class Organization(Schema):
    id = fields.Integer()
    name = fields.String()
    #projects = fields.Nested(Project, many=True)
    #bank_accounts = fields.Nested(BankAccount, many=True)

deserializer = serializer = Organization()

