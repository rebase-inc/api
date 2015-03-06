from marshmallow import fields, Schema
from alveare.models.organization import Organization
from alveare.views.manager import ManagerSchema
from alveare.views.project import ProjectSchema
from alveare.views.bank_account import BankAccountSchema
from alveare.views.user import UserSchema

class OrganizationSchema(Schema):
    id =            fields.Integer()
    name =          fields.String(required=True)
    projects =      fields.Nested(ProjectSchema,        only=('id', 'name'),    many=True)
    bank_account =  fields.Nested(BankAccountSchema,    only=('id',))
    user =          fields.Nested(UserSchema, only='id') #only used for deserialize
    managers =      fields.Nested(ManagerSchema,        only='id',           many=True)

    def make_object(self, data):
        if data.get('id'):
            organization = Organization.query.get(data.get('id', None))
            if not organization:
                raise ValueError('No organization with id {}'.format(data.get('id')))
            return organization
        return Organization(**data)

deserializer = OrganizationSchema(only=('name','user'))
serializer = OrganizationSchema(exclude=('user',))

updater = OrganizationSchema(only=('name', 'projects'))
updater.make_object = lambda data: data
