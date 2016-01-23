from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.github_contributed_repo import GithubContributedRepo


class GithubContributedRepoSchema(RebaseSchema):
    id =                        fields.Integer()
    remote_work_history_id =    fields.Integer()
    account_id =                fields.Integer()
    github_id =                 fields.Integer()
    name =                      fields.String()
    description =               fields.String()
    owner =                     fields.String()

    @post_load
    def make_github_contributed_repo(self, data):
        from rebase.models import GithubContributedRepo
        return self._get_or_make_object(GithubContributedRepo, data)


serializer =            GithubContributedRepoSchema()
deserializer =          GithubContributedRepoSchema(exclude=('id',), strict=True)
update_deserializer =   GithubContributedRepoSchema(context={'raw': True})
