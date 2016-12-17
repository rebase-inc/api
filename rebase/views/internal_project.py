from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.internal_project import InternalProject


class InternalProjectSchema(RebaseSchema):

    id =                fields.Integer()
    name =              fields.String()
    organization =      SecureNestedField('OrganizationSchema',     only=('id','name'), allow_null=True)
    clearances =        SecureNestedField('CodeClearanceSchema',    only=('id',), many=True)
    tickets =           SecureNestedField('TicketSchema',           only=('id',), many=True)
    code_repository =   SecureNestedField('CodeRepositorySchema',   only=('id','url', 'clone'))

    @post_load
    def make_internal_project(self, data):
        return self._get_or_make_object(InternalProject, data)


serializer =            InternalProjectSchema()
deserializer =          InternalProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   InternalProjectSchema(context={'raw': True})
