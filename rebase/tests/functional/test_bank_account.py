from random import randint
from unittest import skip
from functools import partial
from operator import eq, ne
from copy import copy

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.tests.common.bank_account import (
    case_org,
    case_contractors,
)
from rebase.common.utils import RebaseResource, validate_resource_collection

url = 'bank_accounts/{}'.format

def name(res):
    ''' return a name (str) given a contractor or organization object '''
    if 'user' in res.keys():
        user = res['user']
        return user['name']
    elif 'projects' in res.keys():
        return res['name']
    else:
        raise TypeError('res should be Contractor or Organization')

def bank_ownership(resource, op):
    return op(resource['bank_account']['id'], 0)

has_bank =      partial(bank_ownership, op=ne)
has_no_bank =   partial(bank_ownership, op=eq)

class TestBankAccountResource(RebaseRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('bank_accounts')
        self.assertIn('bank_accounts', response)
        accounts = response['bank_accounts']
        self.assertTrue(accounts)

    def create_bank_account(self, owner_type, owner_id, account_title):
        bank_account_data = dict(
            name=account_title,
            routing_number=123450000 + randint(1,9999),
            account_number=12345000 + randint(1,999)
        )
        bank_account_data[owner_type] = dict(id = owner_id)
        response = self.post_resource('bank_accounts', bank_account_data)
        self.assertIn('bank_account', response)
        account = response['bank_account']
        self.assertEqual(account['name'], account_title)
        self.assertEqual(account[owner_type]['id'], owner_id)
        self.assertEqual(account['routing_number'], bank_account_data['routing_number'])
        self.assertEqual(account['account_number'], bank_account_data['account_number'])
        return account

    def find_resource_with_bank_account(self, rest_resource):
        if rest_resource not in ['contractors', 'organizations']:
            raise ValueError('rest_resouce must be "contractors" or "organizations", not "{}"'.format(rest_resource))
        instances = self.get_resource(rest_resource)[rest_resource]
        return next(filter(lambda res: 'bank_account' in res, instances), None)

    def find_resource_without_bank_account(self, rest_resource):
        if rest_resource not in ['contractors', 'organizations']:
            raise ValueError('rest_resouce must be "contractors" or "organizations", not "{}"'.format(rest_resource))
        instances = self.get_resource(rest_resource)[rest_resource]
        return next(filter(lambda res: 'bank_account' not in res, instances), None)

    def test_create_bank_account_for_organization(self):
        self.login_admin()
        org = self.find_resource_without_bank_account('organizations')
        account = self.create_bank_account('organization', org['id'], 'Our Account')
        org_with_account = self.get_resource('organizations/{id}'.format(**org))['organization']
        self.assertEqual(org_with_account['bank_account']['id'], account['id'])

    def test_create_bank_account_for_contractor(self):
        self.login_admin()
        contractor = self.find_resource_without_bank_account('contractors')
        account = self.create_bank_account('contractor', contractor['id'], 'My Account')
        contractor_with_account = self.get_resource('contractors/{id}'.format(**contractor))['contractor']
        self.assertEqual(contractor_with_account['bank_account']['id'], account['id'])

    def delete_bank_account(self, owner_type):
        owner = self.find_resource_without_bank_account('{}s'.format(owner_type))
        account = self.create_bank_account(owner_type, owner['id'], 'Account to be deleted')
        self.delete_resource('bank_accounts/{id}'.format(**account))
        self.get_resource('bank_accounts/{id}'.format(**account), 404)
        same_owner = self.get_resource('{}s/{}'.format(owner_type, owner['id']))[owner_type]
        self.assertNotIn('bank_account', same_owner)

    def test_delete_contractor_bank_account(self):
        self.login_admin()
        self.delete_bank_account('contractor')

    def test_delete_organization_bank_account(self):
        self.login_admin()
        self.delete_bank_account('organization')

    def test_delete_contractor(self):
        self.login_admin()
        contractor = self.find_resource_without_bank_account('contractors')
        account = self.create_bank_account('contractor', contractor['id'], 'Account to be cascade deleted')
        self.delete_resource('contractors/{id}'.format(**contractor))
        self.get_resource('bank_accounts/{id}'.format(**account), 404)

    def test_delete_organization(self):
        self.login_admin()
        org = self.find_resource_without_bank_account('organizations')
        account = self.create_bank_account('organization', org['id'], 'Account to be cascade deleted')
        self.delete_resource('organizations/{id}'.format(**org))
        self.get_resource('bank_accounts/{id}'.format(**account), 404)

    def test_update(self):
        self.login_admin()
        contractor = self.find_resource_with_bank_account('contractors')
        account = self.get_resource('bank_accounts/{id}'.format(**contractor['bank_account']))['bank_account']
        account['name'] = account['name'] + '-UPDATED'

        self.put_resource('bank_accounts/{id}'.format(**account), account)

        updated_account = self.get_resource('bank_accounts/{id}'.format(**account))['bank_account']
        self.assertEqual(account, updated_account)

class TestBankAccount(RebaseNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = RebaseResource(self, 'BankAccount')

    def test_as_manager(self):
        mgr_user, org, account, contractor = case_org(self.db)
        self.login(mgr_user.email, 'foo', 'manager')
        validate_resource_collection(self, [account])
        account_blob = self.resource.get(account.id)
        self.resource.update(**account_blob)
        self.resource.delete(**account_blob)
        del account_blob['id']
        self.resource.create(**account_blob)

    def test_as_contractor(self):
        contractor_0, contractor_1 = case_contractors(self.db)
        self.login(contractor_0.user.email, 'foo', 'contractor')
        validate_resource_collection(self, [contractor_0.bank_account])
        account_0 = self.resource.get(contractor_0.bank_account.id)
        self.resource.update(**account_0)
        self.resource.delete(**account_0)
        new_account = copy(account_0)
        del new_account['id']
        new_account['account_number'] = 9876
        self.resource.create(**new_account)

        self.resource.get(contractor_1.bank_account.id, 401)
        account_1 = copy(account_0)
        account_1['id'] = contractor_1.bank_account.id
        self.resource.update(expected_status=401, **account_1)
        self.resource.delete(expected_status=401, **account_1)
