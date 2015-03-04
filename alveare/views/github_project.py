from marshmallow import fields, Schema
from alveare.models.organization import Organization
from alveare.models.github_project import GithubProject
from alveare.models.code_repository import CodeRepository

class GithubProjectSchema(Schema):
    id = fields.Integer()
    organization_id = fields.Integer()
    name = fields.String()

    def make_object(self, data):
        if data.get('id'):
            # an id is provided, so we're doing an update
            project = GithubProject.query.get_or_404(data['id'])
            project.name = data['name']
            return project
        organization = Organization.query.get_or_404(data['organization_id'])
        project = GithubProject(organization, data['name'])
        CodeRepository(project)
        return project

serializer = GithubProjectSchema(only=('id', 'organization_id', 'name'))
deserializer = GithubProjectSchema(only=('organization_id', 'name'))
update_deserializer = GithubProjectSchema(only=('id', 'organization_id', 'name'))

