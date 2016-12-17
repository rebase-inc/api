from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.organization import Organization
from rebase.views.bank_account import BankAccountSchema
from rebase.views.manager import ManagerSchema
from rebase.views.project import ProjectSchema
from rebase.views.user import UserSchema


class OrganizationSchema(RebaseSchema):
    id =            fields.Integer()
    name =          fields.String()
    projects =      SecureNestedField(ProjectSchema,        only=('id','name'), many=True, allow_null=True)
    bank_account =  SecureNestedField(BankAccountSchema,    only=('id',), allow_null=True)
    user =          SecureNestedField(UserSchema,           only=('id',)) #only used for deserialize
    managers =      SecureNestedField(ManagerSchema,        only=('id','user'), many=True)

    @post_load
    def make_organization(self, data):
        from rebase.models import Organization
        return self._get_or_make_object(Organization, data)


serializer = OrganizationSchema(exclude=('user',))
deserializer = OrganizationSchema(only=('name','user'))
update_deserializer = OrganizationSchema(only=('name',), context={'raw': True})
