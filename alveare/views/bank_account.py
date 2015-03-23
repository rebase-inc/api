from marshmallow import fields
from alveare.common.schema import AlveareSchema
from flask.ext.restful import abort

from alveare.models.bank_account import BankAccount
from alveare.models.organization import Organization
from alveare.models.contractor import Contractor
from alveare.common.database import get_or_make_object

class BankAccountSchema(AlveareSchema):
    id =             fields.Integer()
    name =           fields.String(required=True)
    routing_number = fields.Integer(required=True)
    account_number = fields.Integer(required=True)
    organization =   fields.Nested('OrganizationSchema', only=('id',))
    contractor =     fields.Nested('ContractorSchema', only=('id',))

    def make_object(self, data):
        from alveare.models import BankAccount
        return get_or_make_object(BankAccount, data)

# this is a hack...TODO: GET RID OF IT
@BankAccountSchema.data_handler
def remove_empty_objects(schema, data, obj):
    if isinstance(data, list):
        return [remove_empty_objects(schema, elem, obj) for elem in data]
    if data.get('contractor', None) == dict(id=0):
        data.pop('contractor')
    elif data.get('organization', None) == dict(id=0):
        data.pop('organization')
    return data

serializer = BankAccountSchema(skip_missing=True)
deserializer = BankAccountSchema(exclude=('id',), strict=True)

update_deserializer =   BankAccountSchema(only=('id', 'name',))
update_deserializer.make_object = lambda data: data 

