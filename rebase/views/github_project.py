from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.github_project import GithubProject
from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.views.github_repository import GithubRepositorySchema

class GithubProjectSchema(RebaseSchema):

    id =                fields.Integer()
    name =              fields.String()
    imported =          fields.Boolean()
    organization =      SecureNestedField('GithubOrganizationSchema',   only=('id', 'org_id', 'login', 'url', 'description', 'accounts'), allow_null=True)
    clearances =        SecureNestedField('CodeClearanceSchema',        only=('id',), many=True)
    tickets =           SecureNestedField('GithubTicketSchema',         only=('id',), many=True)
    code_repository =   SecureNestedField(GithubRepositorySchema,       only=('id', 'repo_id', 'name', 'url', 'description', 'project'))

    def make_object(self, data):
        return get_or_make_object(GithubProject, data)


serializer =            GithubProjectSchema(skip_missing=True)
deserializer =          GithubProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   GithubProjectSchema()
update_deserializer.make_object = lambda data: data
