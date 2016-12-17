from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.github_project import GithubProject
from rebase.views.github_repository import GithubRepositorySchema
from rebase.views.work_repo import WorkRepoSchema


class GithubProjectSchema(RebaseSchema):

    id =                fields.Integer()
    name =              fields.String()
    organization =      SecureNestedField('GithubOrganizationSchema',   only=('id', 'org_id', 'login', 'url', 'description', 'accounts'), allow_null=True)
    clearances =        SecureNestedField('CodeClearanceSchema',        only=('id',), many=True)
    tickets =           SecureNestedField('GithubTicketSchema',         only=('id',), many=True)
    work_repo =         SecureNestedField(WorkRepoSchema,               only=('code_repository_id', 'project_id', 'url'))
    remote_repo =       SecureNestedField(GithubRepositorySchema,       only=('id', 'repo_id', 'name', 'url', 'description', 'project'))

    @post_load
    def make_github_project(self, data):
        return self._get_or_make_object(GithubProject, data)


serializer =            GithubProjectSchema()
deserializer =          GithubProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   GithubProjectSchema(context={'raw': True})
