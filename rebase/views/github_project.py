from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.github_project import GithubProject
from rebase.common.database import get_or_make_object, SecureNestedField

class GithubProjectSchema(RebaseSchema):

    id =                fields.Integer()
    name =              fields.String()
    organization =      SecureNestedField('OrganizationSchema',     only=('id',), allow_null=True)
    clearances =        SecureNestedField('CodeClearanceSchema',    only=('id',), many=True)
    tickets =           SecureNestedField('TicketSchema',           only=('id',), many=True)
    code_repository =   SecureNestedField('CodeRepositorySchema',   only=('id',))


    def make_object(self, data):
        return get_or_make_object(GithubProject, data)

serializer =            GithubProjectSchema(skip_missing=True)
deserializer =          GithubProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   GithubProjectSchema()
update_deserializer.make_object = lambda data: data
