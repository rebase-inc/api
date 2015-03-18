from marshmallow import fields, Schema
from alveare.models.organization import Organization
from alveare.views.manager import ManagerSchema
from alveare.views.project import ProjectSchema
from alveare.views.bank_account import BankAccountSchema
from alveare.views.user import UserSchema
from alveare.common.database import get_or_make_object

class OrganizationSchema(Schema):
    id =            fields.Integer()
    name =          fields.String()
    projects =      fields.Nested(ProjectSchema, only=('id',), many=True)
    bank_account =  fields.Nested(BankAccountSchema, only=('id',))
    user =          fields.Nested(UserSchema, only='id') #only used for deserialize
    managers =      fields.Nested(ManagerSchema, only=('id',), many=True)

    def make_object(self, data):
        from alveare.models import Organization
        return get_or_make_object(Organization, data)

# this is a hack...TODO: GET RID OF IT
@OrganizationSchema.data_handler
def remove_empty_bank_account(schema, data, obj):
    if isinstance(data, list):
        return [remove_empty_bank_account(schema, elem, obj) for elem in data]
    if data.get('bank_account', None) == dict(id=0):
        data.pop('bank_account')
    return data

serializer = OrganizationSchema(exclude=('user',))
deserializer = OrganizationSchema(only=('name','user'))

update_deserializer = OrganizationSchema(exclude=('name', 'projects'))
update_deserializer = OrganizationSchema()
update_deserializer.make_object = lambda data: data 
