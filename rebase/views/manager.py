from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema
from rebase.common.database import DB
from rebase.models.manager import Manager
from rebase.models.user import User
from rebase.models.project import Project
from rebase.common.database import get_or_make_object, SecureNestedField

class ManagerSchema(RebaseSchema):
    id =        fields.Integer()
    type =      fields.String()
    project =   SecureNestedField('ProjectSchema',  only=('id','name', 'organization'))
    user =      SecureNestedField('UserSchema',     only=('id',))

    @post_load
    def make_manager(self, data):
        from rebase.models import Manager
        return get_or_make_object(Manager, data)

    def _update_object(self, data):
        from rebase.models import Manager
        return update_object(Manager, data)

serializer =            ManagerSchema()
deserializer =          ManagerSchema(strict=True)
update_deserializer =   ManagerSchema()
update_deserializer.make_object = lambda data: data
