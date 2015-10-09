from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.internal_project import InternalProject
from rebase.common.database import get_or_make_object, SecureNestedField

class InternalProjectSchema(RebaseSchema):

    id =                fields.Integer()
    name =              fields.String()
    organization =      SecureNestedField('OrganizationSchema',     only=('id',), allow_null=True)
    clearances =        SecureNestedField('CodeClearanceSchema',    only=('id',), many=True)
    tickets =           SecureNestedField('TicketSchema',           only=('id',), many=True)
    code_repository =   SecureNestedField('CodeRepositorySchema',   only=('id',))


    def make_object(self, data):
        return get_or_make_object(InternalProject, data)

serializer =            InternalProjectSchema(skip_missing=True)
deserializer =          InternalProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   InternalProjectSchema()
update_deserializer.make_object = lambda data: data