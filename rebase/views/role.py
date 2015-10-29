from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.common.database import get_or_make_object, SecureNestedField

class RoleSchema(RebaseSchema):
    id = fields.Integer()
    type = fields.String()

    user = SecureNestedField('UserSchema', only=('id',))
    project = SecureNestedField('ProjectSchema', only=('id','type','name','organization', 'imported'))
    remote_work_history = SecureNestedField('RemoteWorkHistorySchema', only=('github_repos',))

    def make_object(self, data):
        from rebase.models import Role
        return get_or_make_object(Role, data)

serializer = RoleSchema(only=('id','type','user','roles'), skip_missing=True)

deserializer = RoleSchema(only=tuple(), strict=True)

update_deserializer = RoleSchema(only=tuple())
update_deserializer.make_object = lambda data: data
