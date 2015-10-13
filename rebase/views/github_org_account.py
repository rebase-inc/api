from marshmallow import fields

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.github_org_account import GithubOrgAccount
from rebase.views.github_organization import GithubOrganizationSchema

class GithubOrgAccountSchema(RebaseSchema):
    org_id =        fields.Integer()
    account_id =    fields.Integer()
    org =           SecureNestedField(GithubOrganizationSchema)

    def make_object(self, data):
        from rebase.models import GithubOrgAccount
        return get_or_make_object(GithubOrgAccount, data)


serializer =            GithubOrgAccountSchema()
deserializer =          GithubOrgAccountSchema(exclude=('id',), strict=True)
update_deserializer =   GithubOrgAccountSchema()
update_deserializer.make_object = lambda data: data
