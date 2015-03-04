from marshmallow import fields, Schema
from alveare.common.database import DB
from alveare.models.manager import Manager
from alveare.models.user import User
from alveare.models.organization import Organization

class ManagerSchema(Schema):
    id =                fields.Integer()
    organization_id =   fields.Integer()

    def make_object(self, data):
        user = User.query.get_or_404(data['id'])
        organization = Organization.query.get_or_404(data['organization_id'])
        return Manager(user, organization)

deserializer = serializer = ManagerSchema(only=('id', 'organization_id'))
