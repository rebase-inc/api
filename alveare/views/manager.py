from marshmallow import fields
from alveare.common.schema import AlveareSchema
from alveare.common.database import DB
from alveare.models.manager import Manager
from alveare.models.user import User
from alveare.models.organization import Organization
from alveare.common.database import get_or_make_object, SecureNestedField

class ManagerSchema(AlveareSchema):
    id =           fields.Integer()
    organization = SecureNestedField('OrganizationSchema',  only=('id',), allow_null=True)
    user =         SecureNestedField('UserSchema',          only=('id',), allow_null=True)

    def make_object(self, data):
        from alveare.models import Manager
        return get_or_make_object(Manager, data)

    def _update_object(self, data):
        from alveare.models import Manager
        return update_object(Manager, data)

serializer = ManagerSchema(only=('id','user', 'organization'), skip_missing=True)
deserializer = ManagerSchema(only=('organization','user'))
update_deserializer = ManagerSchema(only=tuple())
update_deserializer.make_object = lambda data: data
