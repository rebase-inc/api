from marshmallow import fields, Schema
from flask.ext.restful import abort

from alveare.models.bank_account import BankAccount
from alveare.models.organization import Organization
from alveare.models.contractor import Contractor

class BankAccountSchema(Schema):
    id =                fields.Integer()
    name =              fields.String()
    routing_number =    fields.Integer()
    account_number =    fields.Integer()
    organization_id =   fields.Integer()
    contractor_id =     fields.Integer()

    def get_owner_and_name(self, data):
        owner = None
        org_id = data.get('organization_id')
        contractor_id = data.get('contractor_id')
        if org_id:
            owner = Organization.query.get_or_404(org_id)
            del data['organization_id']
            if contractor_id:
                abort(400, 'Inconsistent data: both organization_id and contractor_id are provided')
        elif contractor_id:
            owner = Contractor.query.get_or_404(contractor_id)
            del data['contractor_id']
            if org_id:
                abort(400, 'Inconsistent data: both organization_id and contractor_id are provided')
        else:
            abort(400, 'Invalid request: missing organization_id or contractor_id')
        return owner

    def make_object(self, data):
        if data.get('id'):
            # an id is provided, so we're doing an update
            account = BankAccount.query.get_or_404(data['id'])
            data.pop('id')
            for field, value in data.items():
                setattr(account, field, value)
            return account
        owner = self.get_owner_and_name(data)
        account = BankAccount(**data)
        owner.bank_account = account
        return account

deserializer =          BankAccountSchema(exclude=('id'))
update_deserializer =   BankAccountSchema(exclude=('organization_id', 'contractor_id'))
serializer =            BankAccountSchema()
