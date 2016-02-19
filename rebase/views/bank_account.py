from marshmallow import fields, post_load

from rebase.common.schema import RebaseSchema, SecureNestedField


class BankAccountSchema(RebaseSchema):
    id =             fields.Integer()
    name =           fields.String(required=True)
    routing_number = fields.Integer(required=True)
    account_number = fields.Integer(required=True)
    organization =   SecureNestedField('OrganizationSchema', only=('id',), default=None)
    contractor =     SecureNestedField('ContractorSchema', only=('id',), default=None)

    @post_load
    def make_bank_account(self, data):
        from rebase.models import BankAccount
        return self._get_or_make_object(BankAccount, data)


serializer = BankAccountSchema()
deserializer = BankAccountSchema(exclude=('id',), strict=True)
update_deserializer =   BankAccountSchema(only=('id', 'name',), context={'raw': True})

