from marshmallow import fields, post_load
from rebase.common.schema import RebaseSchema

from rebase.common.database import get_or_make_object, SecureNestedField

class RoleSchema(RebaseSchema):
    id = fields.Integer()
    type = fields.String()

    user = SecureNestedField('UserSchema', only=('id',))
    project = SecureNestedField('ProjectSchema', only=('id','type','name','organization')) # only valid for manager roles
    skill_set = SecureNestedField('SkillSetSchema', only=('id','skills'), default=None) # only valid for contractor roles
    remote_work_history = SecureNestedField('RemoteWorkHistorySchema', only=('id','analyzing', 'github_accounts'), default=None) # only valid for contractor roles

    @post_load
    def make_role(self, data):
        from rebase.models import Role
        return self._get_or_make_object(Role, data)

serializer = RoleSchema(only=('id','type','user','roles', 'project', 'skill_set', 'remote_work_history')) # TODO: Use load_only/dump_only
deserializer = RoleSchema(only=tuple(), strict=True)
update_deserializer = RoleSchema(only=tuple(), context={'raw': True})
