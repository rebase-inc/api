from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.github_account import GithubAccount
from rebase.views.github_contributed_repo import GithubContributedRepoSchema
from rebase.views.github_oauth_app import GithubOAuthAppSchema
from rebase.views.github_org_account import GithubOrgAccountSchema
from rebase.views.github_user import GithubUserSchema
from rebase.views.user import UserSchema


class GithubAccountSchema(RebaseSchema):
    app_id =        fields.String()
    github_user_id =fields.Integer()
    user_id =       fields.Integer()
    user =          SecureNestedField(UserSchema, only=('id',), nullable=False)
    github_user =   SecureNestedField(GithubUserSchema, only=('id', 'login', 'name'), nullable=False)
    app =           SecureNestedField(GithubOAuthAppSchema, only=('client_id',), nullable=False)
    orgs =          SecureNestedField(GithubOrgAccountSchema, many=True, only=('org_id', 'app_id', 'github_user_id', 'user_id'), nullable=True)
    contributed_repos = SecureNestedField(GithubContributedRepoSchema, many=True, nullable=True)

    @post_load
    def make_github_account(self, data):
        from rebase.models import GithubAccount
        return self._get_or_make_object(GithubAccount, data)


serializer =            GithubAccountSchema()
deserializer =          GithubAccountSchema(exclude=('app_id', 'github_user_id', 'user_id'), strict=True)
update_deserializer =   GithubAccountSchema(context={'raw': True})
