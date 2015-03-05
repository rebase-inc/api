from marshmallow import fields, Schema
from alveare.common.database import DB
from alveare.models.project import Project
from alveare.models.user import User
from alveare.models.organization import Organization

class ProjectSchema(Schema):
    id =                fields.Integer()
    organization_id =   fields.Integer()
    name =              fields.String()
    type =              fields.String()

    def make_object(self, data):
        if data.get('id'):
            # an id is provided, so we're doing an update
            project = Project.query.get_or_404(data['id'])
            project.name = data['name']
            return project
        organization = Organization.query.get_or_404(data['organization_id'])
        project = Project(organization, data['name'])
        CodeRepository(project)
        return project

serializer = ProjectSchema()
deserializer = ProjectSchema(only=('organization_id', 'name'))
update_deserializer = ProjectSchema()
