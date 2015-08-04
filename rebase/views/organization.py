from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.organization import Organization
from rebase.views.manager import ManagerSchema
from rebase.views.project import ProjectSchema
from rebase.views.bank_account import BankAccountSchema
from rebase.views.user import UserSchema
from rebase.common.database import get_or_make_object, SecureNestedField

class OrganizationSchema(RebaseSchema):
    id =            fields.Integer()
    name =          fields.String()
    projects =      SecureNestedField(ProjectSchema,        only=('id',), many=True, allow_null=True)
    bank_account =  SecureNestedField(BankAccountSchema,    only=('id',), allow_null=True)
    user =          SecureNestedField(UserSchema,           only=('id',)) #only used for deserialize
    managers =      SecureNestedField(ManagerSchema,        only=('id','user'), many=True)

    def make_object(self, data):
        from rebase.models import Organization
        return get_or_make_object(Organization, data)

serializer = OrganizationSchema(exclude=('user',), skip_missing=True)
deserializer = OrganizationSchema(only=('name','user'))

update_deserializer = OrganizationSchema(only=('name',))
update_deserializer.make_object = lambda data: data
