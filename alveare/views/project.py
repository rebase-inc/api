from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import DB
from alveare.models.project import Project
from alveare.models.user import User
from alveare.models.organization import Organization
from alveare.common.database import get_or_make_object, SecureNestedField
from alveare.views.ticket import TicketSchema

class ProjectSchema(AlveareSchema):
    id =                fields.Integer()
    name =              fields.String()
    type =              fields.String()
    organization =      SecureNestedField('OrganizationSchema', only=('id',))
    clearances =        SecureNestedField('CodeClearanceSchema', only=('id',), many=True)
    tickets =           SecureNestedField('TicketSchema', only=('id',), many=True)
    code_repository =   SecureNestedField('CodeRepositorySchema', only=('id',))

    def make_object(self, data):
        from alveare.models import Project
        return get_or_make_object(Project, data)

serializer = ProjectSchema()
deserializer = ProjectSchema(only=('organization', 'name'))
update_deserializer = ProjectSchema()
update_deserializer.make_object = lambda data: data

