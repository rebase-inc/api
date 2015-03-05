from marshmallow import fields, Schema
from alveare.models.organization import Organization
from alveare.views.manager import ManagerSchema
from alveare.views.project import ProjectSchema
from alveare.views.bank_account import BankAccountSchema

class OrganizationSchema(Schema):
    id =            fields.Integer()
    name =          fields.String(required=True)
    projects =      fields.Nested(ProjectSchema,        only=('id', 'name'),    many=True)
    managers =      fields.Nested(ManagerSchema,        only=('id',),           many=True)
    bank_account =  fields.Nested(BankAccountSchema,    only=('id',))

    def make_object(self, data):
        if data.get('id'):
            # an id is provided, so we're doing an update
            org = Organization.query.get_or_404(data['id'])
            org.name = data['name']
            return org
        return Organization(**data)

deserializer =          OrganizationSchema(only=('name',))
update_deserializer =   OrganizationSchema(only=('id', 'name'))
serializer =            OrganizationSchema()
