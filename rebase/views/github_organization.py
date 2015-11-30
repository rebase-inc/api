from marshmallow import fields, post_load

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.github_organization import GithubOrganization

class GithubOrganizationSchema(RebaseSchema):
    id =            fields.Integer()
    org_id =        fields.Integer()
    login =         fields.String()
    url =           fields.String()
    description =   fields.String()

    projects =      SecureNestedField('GithubProjectSchema', many=True)
    accounts =      SecureNestedField('GithubOrgAccountSchema', only=('account_id',), many=True)

    @post_load
    def make_github_organization(self, data):
        from rebase.models import GithubOrganization
        return get_or_make_object(GithubOrganization, data)


serializer =            GithubOrganizationSchema()
deserializer =          GithubOrganizationSchema(exclude=('id'), strict=True)
update_deserializer =   GithubOrganizationSchema()
update_deserializer.make_object = lambda data: data
