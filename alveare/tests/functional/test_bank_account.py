from . import AlveareRestTestCase
from random import randint
from unittest import skip
from functools import partial
from operator import eq, ne

url = 'bank_accounts/{}'.format

def name(res):
    ''' return a name (str) given a contractor or organization object '''
    if 'user' in res.keys():
        user = res['user']
        return user['first_name']+' '+user['last_name']
    elif 'projects' in res.keys():
        return res['name']
    else:
        raise TypeError('res should be Contractor or Organization')

def bank_ownership(resource, op):
    return op(resource['bank_account']['id'], 0)

has_bank =      partial(bank_ownership, op=ne)
has_no_bank =   partial(bank_ownership, op=eq)

class TestBankAccountResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('bank_accounts')
        self.assertIn('bank_accounts', response)
        accounts = response['bank_accounts']
        self.assertTrue(accounts)

    def create_bank_account(self, owner_type, owner, owner_name):
        bank_account_data = dict(
            name=owner_name,
            routing_number=123450000+randint(1,9999),
            account_number=12345000+randint(1,999)
        )
        bank_account_data[owner_type] = owner
        response = self.post_resource('bank_accounts', bank_account_data)
        self.assertIn('bank_account', response)
        account = response['bank_account']
        self.assertEqual(account['name'], owner_name)
        self.assertEqual(account[owner_type]['id'], owner['id'])
        self.assertEqual(account['routing_number'], bank_account_data['routing_number'])
        self.assertEqual(account['account_number'], bank_account_data['account_number'])
        return account

    def find_resource(self, resources, bank_ownership):
        '''
        resources can either be 'organizations' or 'contractors'
        bank_ownership is a function that returns a boolean given a resource
        '''
        response = self.get_resource(resources)
        self.assertIn(resources, response)
        all_resources = response[resources]
        matching_resources = list(filter(lambda resource: bank_ownership(resource), all_resources))
        self.assertTrue(matching_resources)
        return matching_resources[0]

    def find_resource_with_bank_account(self, resources):
        return self.find_resource(resources, has_bank)

    def find_resource_with_no_bank_account(self, resources):
        return self.find_resource(resources, has_no_bank)

    def test_create_org_account(self):
        org = self.find_resource_with_no_bank_account('organizations')
        account = self.create_bank_account('organization', dict(id=org['id']), org['name'])

        updated_org = self.get('organization', org['id'])
        self.assertEqual(updated_org['bank_account']['id'], account['id'])

    def test_contractor_account(self):
        contractor = self.find_resource_with_no_bank_account('contractors')
        account = self.create_bank_account('contractor', dict(id=contractor['id']), name(contractor))

        updated_contractor = self.get('contractor', contractor['id'])
        self.assertEqual(updated_contractor['bank_account']['id'], account['id'])

    def delete_bank_account(self, resource, name_fn):
        '''
        resource can be 'organization' or 'contractor'
        name_fn is a function that, given an instance of a resource, returns a name (str)
        '''
        owner = self.find_resource_with_no_bank_account('{}s'.format(resource))
        account = self.create_bank_account('{}'.format(resource), dict(id=owner['id']), name_fn(owner))
        account_url = url(account['id'])
        self.delete_resource(account_url)
        self.get_resource(account_url, 404)
        same_owner = self.get(resource, owner['id'])
        self.assertEqual(same_owner['bank_account']['id'], 0)


    def test_delete_contractor_bank_account(self):
        self.delete_bank_account('contractor', name)

    def test_delete_organization_bank_account(self):
        self.delete_bank_account('organization', name)

    def test_delete_contractor(self):
        contractor = self.find_resource_with_no_bank_account('contractors')
        account = self.create_bank_account('contractor', dict(id=contractor['id']), name(contractor))
        account_url = url(account['id'])
        self.delete_resource('contractors/{}'.format(contractor['id']))
        self.get_resource(account_url, 404)

    def test_delete_organization(self):
        org = self.find_resource_with_no_bank_account('organizations')
        account = self.create_bank_account('organization', dict(id=org['id']), name(org))
        account_url = url(account['id'])
        self.delete_resource('organizations/{}'.format(org['id']))
        self.get_resource(account_url, 404)

    def test_update(self):
        contractor = self.find_resource_with_bank_account('contractors')
        account = self.get('bank_account', contractor['bank_account']['id'])

        account['name'] = account['name'] + 'XXXXX'

        self.put_resource(url(account['id']), account)

        updated_account = self.get('bank_account', account['id'])
        self.assertEqual(account, updated_account)
