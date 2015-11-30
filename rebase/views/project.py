from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.models.project import Project
from rebase.common.database import get_or_make_object, SecureNestedField

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

    def make_object(self, data):
        return get_or_make_object(Project, data)


serializer =            ProjectSchema()
deserializer =          ProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   ProjectSchema()
update_deserializer.make_object = lambda data: data

