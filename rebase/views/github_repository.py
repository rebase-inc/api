from marshmallow import fields, post_load

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.github_repository import GithubRepository
from rebase.views.github_organization import GithubOrganizationSchema

class GithubRepositorySchema(RebaseSchema):
    id =            fields.Integer()
    repo_id =       fields.Integer()
    name =          fields.String()
    url =           fields.String()
    description =   fields.String()

    project =       fields.Nested('GithubProjectSchema', only=('organization', 'id'))

    @post_load
    def make_github_repository(self, data):
        from rebase.models import GithubRepository
        return get_or_make_object(GithubRepository, data)

serializer =            GithubRepositorySchema()
deserializer =          GithubRepositorySchema(exclude=('id'), strict=True)
update_deserializer =   GithubRepositorySchema()
update_deserializer.make_object = lambda data: data
