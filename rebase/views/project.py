from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.project import Project


class ProjectSchema(RebaseSchema):

    id =                fields.Integer()
    name =              fields.String()
    deploy =            fields.String()
    test =              fields.String()
    readme =            fields.String()
    organization =      SecureNestedField('OrganizationSchema',     only=('id','name'))
    clearances =        SecureNestedField('CodeClearanceSchema',    only=('id',), many=True)
    tickets =           SecureNestedField('TicketSchema',           only=('id',), many=True)
    work_repo =         SecureNestedField('WorkRepoSchema',         only=('id', 'url', 'clone'))
    type =              fields.String()

    @post_load
    def make_project(self, data):
        return self._get_or_make_object(Project, data)


serializer =            ProjectSchema()
deserializer =          ProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   ProjectSchema(context={'raw': True})
