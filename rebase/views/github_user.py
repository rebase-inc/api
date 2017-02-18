from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.github_account import GithubAccount


class GithubUserSchema(RebaseSchema):
    id =        fields.Integer()
    login =     fields.String()
    name =      fields.String()
    out_of_date = fields.Boolean()
    accounts =   SecureNestedField('GithubAccountSchema', only=('app_id', 'github_user_id', 'user_id'), many=True)

    @post_load
    def make_github_user(self, data):
        from rebase.models import GithubUser
        return self._get_or_make_object(GithubUser, data)


serializer =            GithubUserSchema()
deserializer =          GithubUserSchema(exclude=('app_id', 'github_user_id', 'user_id'), strict=True)
update_deserializer =   GithubUserSchema(context={'raw': True})
