from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.organization import Organization
from alveare.views.manager import ManagerSchema
from alveare.views.project import ProjectSchema
from alveare.views.bank_account import BankAccountSchema
from alveare.views.user import UserSchema
from alveare.common.database import get_or_make_object, SecureNestedField

class OrganizationSchema(AlveareSchema):
    id =            fields.Integer()
    name =          fields.String()
    projects =      SecureNestedField(ProjectSchema, only=('id',), many=True)
    bank_account =  SecureNestedField(BankAccountSchema, only=('id',), default=None)
    user =          SecureNestedField(UserSchema, only=('id',)) #only used for deserialize
    managers =      SecureNestedField(ManagerSchema, only=('id','user'), many=True)

    def make_object(self, data):
        from alveare.models import Organization
        return get_or_make_object(Organization, data)

serializer = OrganizationSchema(exclude=('user',), skip_missing=True)
deserializer = OrganizationSchema(only=('name','user'))

update_deserializer = OrganizationSchema(only=('name',))
update_deserializer.make_object = lambda data: data
