from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.github_org_account import GithubOrgAccount
from rebase.views.github_organization import GithubOrganizationSchema


class GithubOrgAccountSchema(RebaseSchema):
    org_id =            fields.Integer()
    app_id =            fields.String()
    github_user_id =    fields.Integer()
    user_id =           fields.Integer()

    org =               SecureNestedField(GithubOrganizationSchema, only=('id',))
    account =           SecureNestedField('GithubAccountSchema', only=('app_id', 'github_user_id', 'user_id'))

    @post_load
    def make_github_org_account(self, data):
        from rebase.views.github_account import GithubAccountSchema
        return self._get_or_make_object(GithubOrgAccount, data)


serializer =            GithubOrgAccountSchema()
deserializer =          GithubOrgAccountSchema(exclude=('org_id', 'app_id', 'github_user_id', 'user_id'), strict=True)
update_deserializer =   GithubOrgAccountSchema(context={'raw': True})
