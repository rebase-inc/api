from marshmallow import fields, post_load
import marshmallow.exceptions as marsh

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.views.role import RoleSchema
from rebase.views.ssh_key import SSHKeySchema

class PhotoSchema(RebaseSchema):
    id =  fields.Integer()
    url = fields.String(required=True)

class UserSchema(RebaseSchema):

    id =            fields.Integer()
    name =          fields.String(required=False)
    email =         fields.Email(required=True)
    password =      fields.String(required=True)
    last_seen =     fields.DateTime(required=True, dump_only=True)
    admin =         fields.Boolean(default=False, dump_only=True)

    roles = SecureNestedField('RoleSchema', exclude=('user',), many=True)
    current_role =  SecureNestedField('RoleSchema')
    photo =         SecureNestedField(PhotoSchema, only='url', dump_only=True)
    ssh_public_keys = SecureNestedField(SSHKeySchema, exclude=('user',), many=True)
    github_accounts = SecureNestedField('GithubAccountSchema', exclude=('user',), many=True)

    @post_load
    def make_user(self, data):
        from rebase.models import User
        if 'email' in data:
            user = User.query.filter(User.email == data.get('email')).first()
            if not user:
                raise marsh.ValidationError('Bad email', fields=['email',])
            return user
        return self._get_or_make_object(User, data)

serializer = UserSchema()
deserializer = UserSchema(strict=True)
update_deserializer = UserSchema(context={'raw': True})
