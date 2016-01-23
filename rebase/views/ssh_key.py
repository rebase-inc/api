from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField
from rebase.models.ssh_key import SSHKey


class SSHKeySchema(RebaseSchema):

    id =            fields.Integer(dump_only=True)
    user_id =       fields.Integer()
    title =         fields.String()
    key =           fields.String(load_only=True)
    fingerprint =   fields.String(dump_only=True)

    user =          SecureNestedField('UserSchema', only=('id',), required=True)

    @post_load
    def make_ssh_key(self, data):
        from rebase.models import SSHKey
        return self._get_or_make_object(SSHKey, data)

serializer =            SSHKeySchema()
deserializer =          SSHKeySchema(strict=True)
update_deserializer =   SSHKeySchema(context={'raw': True})
