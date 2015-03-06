from . import AlveareRestTestCase
from random import randint
from unittest import skip

url = 'bank_accounts/{}'.format

class TestBankAccountResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('bank_accounts')
        self.assertIn('bank_accounts', response)
        accounts = response['bank_accounts']
        self.assertTrue(accounts)

    def create_bank_account(self, owner_id_key, owner_id_value, owner_name):
        account_data = dict(name=owner_name, routing_number=123450000+randint(1,9999), account_number=12345000+randint(1,999))
        account_data[owner_id_key] = owner_id_value
        response = self.post_resource('bank_accounts', account_data)
        self.assertIn('bank_account', response)
        account = response['bank_account']
        self.assertEqual(account['name'], owner_name)
        self.assertEqual(account[owner_id_key], owner_id_value)
        self.assertEqual(account['routing_number'], account_data['routing_number'])
        self.assertEqual(account['account_number'], account_data['account_number'])
        return account

    def find_org_with_no_bank_account(self):
        orgs = self.get_resource('organizations')['organizations']
        self.assertTrue(orgs)
        no_account_orgs = list(filter(lambda org: org['bank_account']==0, orgs))
        self.assertTrue(no_account_orgs)
        return no_account_orgs[0]

    def find_contractor_with_no_bank_account(self):
        contractors = self.get_resource('contractors')['contractors']
        self.assertTrue(contractors)
        no_account_contractors = list(filter(lambda c: c['bank_account']==0, contractors))
        self.assertTrue(no_account_contractors)
        return no_account_contractors[0]

    def get_org(self, org_id):
        return self.get_resource('organizations/{}'.format(org_id))['organization']

    def get_contractor(self, contractor_id):
        return self.get_resource('contractors/{}'.format(contractor_id))['contractor']

    def test_create_org_account(self):
        org = self.find_org_with_no_bank_account()
        account = self.create_bank_account('organization_id', org['id'], org['name'])

        updated_org = self.get_org(org['id'])
        self.assertEqual(updated_org['bank_account'], account['id'])

    #@skip('TODO: implement the Contractor resource')
    def test_create_contractor_account(self):
        contractor = self.find_contractor_with_no_bank_account()
        account = self.create_bank_account('contractor_id', contractor['id'], contractor['user']['first_name']+' '+contractor['user']['last_name'])

        updated_contractor = self.get_contractor(contractor['id'])
        self.assertEqual(updated_contractor['bank_account'], account['id'])

