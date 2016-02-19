from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema
from rebase.models.github_account import GithubAccount
from rebase.views.github_org_account import GithubOrgAccountSchema
from rebase.views.github_contributed_repo import GithubContributedRepoSchema


class GithubAccountSchema(RebaseSchema):
    id =            fields.Integer()
    login =         fields.String()
    access_token =  fields.String()
    orgs =          fields.Nested(GithubOrgAccountSchema, many=True, nullable=True)
    contributed_repos = fields.Nested(GithubContributedRepoSchema, many=True, nullable=True)

    @post_load
    def make_github_account(self, data):
        from rebase.models import GithubAccount
        return self._get_or_make_object(GithubAccount, data)


serializer =            GithubAccountSchema()
deserializer =          GithubAccountSchema(exclude=('id',), strict=True)
update_deserializer =   GithubAccountSchema(context={'raw': True})
