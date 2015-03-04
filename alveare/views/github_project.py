from marshmallow import fields, Schema
from alveare.models.organization import Organization
from alveare.models.github_project import GithubProject

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
        return GithubProject(organization, data['name'])

serializer = GithubProjectSchema(only=('id', 'organization_id', 'name'))
deserializer = GithubProjectSchema(only=('organization_id', 'name'))

