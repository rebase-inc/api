from marshmallow import fields

from rebase.common.database import get_or_make_object, SecureNestedField
from rebase.common.schema import RebaseSchema
from rebase.models.ssh_key import SSHKey

class SSHKeySchema(RebaseSchema):
    id =            fields.Integer()
    user_id =       fields.Integer()
    title =         fields.String()
    key =           fields.String()
    fingerprint =   fields.String()

    user =          SecureNestedField('UserSchema', only=('id',), required=True)

    def make_object(self, data):
        from rebase.models import SSHKey
        return get_or_make_object(SSHKey, data)


serializer =            SSHKeySchema()
deserializer =          SSHKeySchema(exclude=('id',), strict=True)
update_deserializer =   SSHKeySchema()
update_deserializer.make_object = lambda data: data
