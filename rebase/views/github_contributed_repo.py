from marshmallow import fields

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.github_contributed_repo import GithubContributedRepo

class GithubContributedRepoSchema(RebaseSchema):
    id =                        fields.Integer()
    remote_work_history_id =    fields.Integer()
    account_id =                fields.Integer()
    github_id =                 fields.Integer()
    name =                      fields.String()
    description =               fields.String()
    owner =                     fields.String()

    def make_object(self, data):
        from rebase.models import GithubContributedRepo
        return get_or_make_object(GithubContributedRepo, data)


serializer =            GithubContributedRepoSchema()
deserializer =          GithubContributedRepoSchema(exclude=('id',), strict=True)
update_deserializer =   GithubContributedRepoSchema()
update_deserializer.make_object = lambda data: data
