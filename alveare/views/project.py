from marshmallow import fields
from rebase.common.schema import AlveareSchema
from rebase.models.project import Project
from rebase.common.database import get_or_make_object, SecureNestedField

class ProjectSchema(AlveareSchema):

    id =                fields.Integer()
    name =              fields.String()
    organization =      SecureNestedField('OrganizationSchema',     only=('id',), allow_null=True)
    clearances =        SecureNestedField('CodeClearanceSchema',    only=('id',), many=True)
    tickets =           SecureNestedField('TicketSchema',           only=('id',), many=True)
    code_repository =   SecureNestedField('CodeRepositorySchema',   only=('id',))
    type =              fields.String()

    def make_object(self, data):
        return get_or_make_object(Project, data)

serializer =            ProjectSchema(skip_missing=True)
deserializer =          ProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   ProjectSchema()
update_deserializer.make_object = lambda data: data

