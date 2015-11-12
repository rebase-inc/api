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
    work_repo =         SecureNestedField('WorkRepoSchema',         only=('id', 'url'))
    type =              fields.String()

    def make_object(self, data):
        return get_or_make_object(Project, data)

def add_clone(project):
    url = project['work_repo']['url']
    project['clone'] = 'git clone {}'.format(url)
    return project

@ProjectSchema.data_handler
def make_clone_command(serializer, data, obj):
    if isinstance(obj, list):
        data = list(map(add_clone, data))
    else:
        data = add_clone(data)
    return data

serializer =            ProjectSchema(skip_missing=True)
deserializer =          ProjectSchema(only=('organization', 'name'), strict=True)
update_deserializer =   ProjectSchema()
update_deserializer.make_object = lambda data: data

