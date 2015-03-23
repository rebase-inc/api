from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import DB
from alveare.models.project import Project
from alveare.models.user import User
from alveare.models.organization import Organization
from alveare.common.database import get_or_make_object
from alveare.views.ticket import TicketSchema

class ProjectSchema(AlveareSchema):
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

serializer = ProjectSchema()
deserializer = ProjectSchema(only=('organization', 'name'))
update_deserializer = ProjectSchema()
update_deserializer.make_object = lambda data: data

