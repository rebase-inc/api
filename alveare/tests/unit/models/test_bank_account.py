from . import AlveareModelTestCase

from alveare import models
from alveare.tests.common.bank_account import (
    case_contractors,
    case_org,
)
from alveare.common import mock

class TestBankAccountModel(AlveareModelTestCase):
    model = models.BankAccount

    def test_create(self):
        routing = 123456789
        account = 123412341234
        new_bank_account = self.create_model(self.model, 'Joe Blow', routing, account)
        self.assertEqual(new_bank_account.routing_number, routing)
        self.assertEqual(new_bank_account.account_number, account)

    def test_delete(self):
        new_bank_account = self.create_model(self.model, 'Elon Musk', 123456789, 12345678901234567)
        self.delete_instance(new_bank_account)

    def test_update(self):
        first_routing = 112112112
        second_routing = 113113113
        new_bank_account = self.create_model(self.model, 'Raphael Goyran', first_routing, 1)
        self.assertEqual(new_bank_account.routing_number, first_routing)
        self.assertEqual(new_bank_account.account_number, 1)

        new_bank_account.routing_number = second_routing
        new_bank_account.account_number = 2
        self.db.session.commit()

        modified_bank_account = self.model.query.get(new_bank_account.id)
        self.assertEqual(modified_bank_account.routing_number, second_routing)
        self.assertEqual(modified_bank_account.account_number, 2)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'Yo Mama', 'foo', 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'Yo Mama', 1234, 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'Yo Mama', 123456789, 'foo')

    def test_as_admin(self):
        mgr_user, org, account, contractor = case_org(self.db)
        _, _, account2, _ = case_org(self.db) # create more orgs with bank accounts
        admin = mock.create_admin_user(self.db, 'foo')
        self.assertTrue(account.allowed_to_be_viewed_by(admin))
        self.assertTrue(account.allowed_to_be_modified_by(admin))
        self.assertTrue(account.allowed_to_be_created_by(admin))
        self.assertTrue(account.allowed_to_be_deleted_by(admin))

        all_accounts = models.BankAccount.query_by_user(admin).all()
        self.assertEqual([account, account2], all_accounts)

    def test_as_contractor(self):
        contractors = case_contractors(self.db)
        contractor = contractors[0]
        
        self.assertTrue(contractor.bank_account.allowed_to_be_viewed_by(contractor.user))
        self.assertTrue(contractor.bank_account.allowed_to_be_modified_by(contractor.user))
        self.assertTrue(contractor.bank_account.allowed_to_be_created_by(contractor.user))
        self.assertTrue(contractor.bank_account.allowed_to_be_deleted_by(contractor.user))

        some_dude = mock.create_one_user(self.db)
        self.assertFalse(contractor.bank_account.allowed_to_be_viewed_by(some_dude))
        self.assertFalse(contractor.bank_account.allowed_to_be_modified_by(some_dude))
        self.assertFalse(contractor.bank_account.allowed_to_be_created_by(some_dude))
        self.assertFalse(contractor.bank_account.allowed_to_be_deleted_by(some_dude))

        self.assertEqual([contractor.bank_account], models.BankAccount.as_contractor(contractor.user).all())
        self.assertEqual([contractor.bank_account], models.BankAccount.get_all(contractor.user).all())

    def test_as_manager(self):
        mgr_user, org, account, contractor = case_org(self.db)
        case_org(self.db) # create more orgs with bank accounts
        
        self.assertTrue(account.allowed_to_be_viewed_by(mgr_user))
        self.assertTrue(account.allowed_to_be_modified_by(mgr_user))
        self.assertTrue(account.allowed_to_be_created_by(mgr_user))
        self.assertTrue(account.allowed_to_be_deleted_by(mgr_user))
        self.assertFalse(account.allowed_to_be_viewed_by(contractor.user))
        self.assertFalse(account.allowed_to_be_modified_by(contractor.user))
        self.assertFalse(account.allowed_to_be_created_by(contractor.user))
        self.assertFalse(account.allowed_to_be_deleted_by(contractor.user))
        some_dude = mock.create_one_user(self.db)
        self.assertFalse(account.allowed_to_be_viewed_by(some_dude))
        self.assertFalse(account.allowed_to_be_modified_by(some_dude))
        self.assertFalse(account.allowed_to_be_created_by(some_dude))
        self.assertFalse(account.allowed_to_be_deleted_by(some_dude))
        self.assertEqual([account], models.BankAccount.as_manager(mgr_user).all())
        self.assertEqual([account], models.BankAccount.get_all(mgr_user).all())

    def test_get_all_as_user(self):
        case_org(self.db)
        case_org(self.db)
        user = mock.create_one_user(self.db)
        accounts = models.BankAccount.get_all(user).all()
        self.assertFalse(accounts)

