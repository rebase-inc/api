from marshmallow import fields
from rebase.common.schema import RebaseSchema

from rebase.common.database import get_or_make_object, SecureNestedField

class BankAccountSchema(RebaseSchema):
    id =             fields.Integer()
    name =           fields.String(required=True)
    routing_number = fields.Integer(required=True)
    account_number = fields.Integer(required=True)
    organization =   SecureNestedField('OrganizationSchema', only=('id',), default=None)
    contractor =     SecureNestedField('ContractorSchema', only=('id',), default=None)

    def make_object(self, data):
        from rebase.models import BankAccount
        return get_or_make_object(BankAccount, data)

serializer = BankAccountSchema(skip_missing=True)
deserializer = BankAccountSchema(exclude=('id',), strict=True)

update_deserializer =   BankAccountSchema(only=('id', 'name',))
update_deserializer.make_object = lambda data: data

