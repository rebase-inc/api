from marshmallow import fields, Schema
from alveare.models.organization import Organization

class OrganizationSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    #projects = fields.Nested(Project, many=True)
    #bank_accounts = fields.Nested(BankAccount, many=True)

    def make_object(self, data):
        if data.get('id'):
            # an id is provided, so we're doing an update
            org = Organization.query.get_or_404(data['id'])
            org.name = data['name']
            return org
        return Organization(**data)

deserializer = OrganizationSchema(only=('name',))
update_deserializer = OrganizationSchema(only=('id', 'name'))
serializer = OrganizationSchema(only=('id', 'name'))

