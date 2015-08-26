from marshmallow import fields
from rebase.common.schema import RebaseSchema
from rebase.common.database import DB
from rebase.models.manager import Manager
from rebase.models.user import User
from rebase.models.organization import Organization
from rebase.common.database import get_or_make_object, SecureNestedField

class ManagerSchema(RebaseSchema):
    id =           fields.Integer()
    organization = SecureNestedField('OrganizationSchema',  only=('id','name'), allow_null=True)
    user =         SecureNestedField('UserSchema',          only=('id',), allow_null=True)

    def make_object(self, data):
        from rebase.models import Manager
        return get_or_make_object(Manager, data)

    def _update_object(self, data):
        from rebase.models import Manager
        return update_object(Manager, data)

serializer =            ManagerSchema(skip_missing=True)
deserializer =          ManagerSchema(strict=True)
update_deserializer =   ManagerSchema()
update_deserializer.make_object = lambda data: data
