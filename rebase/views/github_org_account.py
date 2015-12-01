from marshmallow import fields, post_load

from rebase.common.database import SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.github_org_account import GithubOrgAccount
from rebase.views.github_organization import GithubOrganizationSchema

class GithubOrgAccountSchema(RebaseSchema):
    org_id =        fields.Integer()
    account_id =    fields.Integer()
    org =           SecureNestedField(GithubOrganizationSchema)

    @post_load
    def make_github_org_account(self, data):
        from rebase.models import GithubOrgAccount
        return self._get_or_make_object(GithubOrgAccount, data)


serializer =            GithubOrgAccountSchema()
deserializer =          GithubOrgAccountSchema(exclude=('id',), strict=True)
update_deserializer =   GithubOrgAccountSchema(context={'raw': True})
