from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.models.organization import Organization
from alveare.models.github_project import GithubProject
from alveare.models.code_repository import CodeRepository
from alveare.common.database import get_or_make_object

class GithubProjectSchema(AlveareSchema):

    id =              fields.Integer()
    name =            fields.String()
    organization =    fields.Nested('OrganizationSchema', only=('id',), required=True)
    code_repository = fields.Nested('CodeRepositorySchema', only=('id',))
    tickets =         fields.Nested('TicketSchema', only=('id',))
    clearances =      fields.Nested('CodeClearanceSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import GithubProject
        return get_or_make_object(GithubProject, data)

serializer =            GithubProjectSchema(only=('id', 'organization', 'name'), skip_missing=True)
deserializer =          GithubProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   GithubProjectSchema(only=tuple())
update_deserializer.make_object = lambda data: data
