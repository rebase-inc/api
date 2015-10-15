from marshmallow import fields

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.github_account import GithubAccount
from rebase.views.github_org_account import GithubOrgAccountSchema

class GithubAccountSchema(RebaseSchema):
    id =            fields.Integer()
    login =         fields.String()
    access_token =  fields.String()
    orgs =          fields.Nested(GithubOrgAccountSchema, many=True, nullable=True)

    def make_object(self, data):
        from rebase.models import GithubAccount
        return get_or_make_object(GithubAccount, data)


serializer =            GithubAccountSchema()
deserializer =          GithubAccountSchema(exclude=('id',), strict=True)
update_deserializer =   GithubAccountSchema()
update_deserializer.make_object = lambda data: data
