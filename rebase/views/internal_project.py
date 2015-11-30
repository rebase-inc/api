from marshmallow import fields, post_load
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

    @post_load
    def make_internal_project(self, data):
        return get_or_make_object(InternalProject, data)

serializer =            InternalProjectSchema()
deserializer =          InternalProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   InternalProjectSchema()
update_deserializer.make_object = lambda data: data
