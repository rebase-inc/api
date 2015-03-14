from marshmallow import fields, Schema
from alveare.common.database import DB
from alveare.models.project import Project
from alveare.models.user import User
from alveare.models.organization import Organization
from alveare.common.resource import get_or_make_object, update_object

class ProjectSchema(Schema):
    id =                fields.Integer()
    organization =      fields.Nested('OrganizationSchema', only=('id',))
    name =              fields.String()
    type =              fields.String()
    clearances =        fields.Nested('CodeClearanceSchema', only=('id',), many=True)
    tickets =           fields.Nested('TicketSchema', only=('id',), many=True)
    code_repository =   fields.Nested('CodeRepositorySchema', only=('id',))

    def make_object(self, data):
        from alveare.models import Project
        return get_or_make_object(Project, data)

    def _update_object(self, data):
        from alveare.models import Project
        return update_object(Project, data)

serializer = ProjectSchema()
deserializer = ProjectSchema(only=('organization_id', 'name'))
update_deserializer = ProjectSchema()
update_deserializer.make_object = update_deserializer._update_object

