from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.github_account import GithubAccount


class GithubOAuthAppSchema(RebaseSchema):
    #client_id = fields.String()
    name =      fields.String()
    url =       fields.String()
    accounts =  SecureNestedField('GithubAccountSchema', only=('app_id', 'github_user_id', 'user_id'), many=True)

    @post_load
    def make_github_user(self, data):
        from rebase.models import GithubOAuthApp
        return self._get_or_make_object(GithubOAuthApp, data)


serializer =            GithubOAuthAppSchema()
deserializer =          GithubOAuthAppSchema(exclude=('client_id',), strict=True)
update_deserializer =   GithubOAuthAppSchema(context={'raw': True})
