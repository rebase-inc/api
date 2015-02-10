from . import AlveareModelTestCase

from alveare import models

class TestBankAccountModel(AlveareModelTestCase):
    model = models.BankAccount

    def test_create(self):
        routing = 123456789
        account = 123412341234
        new_bank_account = self.create_model(self.model, routing, account)
        self.assertEqual(new_bank_account.routing_number, routing)
        self.assertEqual(new_bank_account.account_number, account)

    def test_delete(self):
        new_bank_account = self.create_model(self.model, 111111111, 22222222222)
        self.delete_instance(self.model, new_bank_account)

    def test_update(self):
        first_routing = 112112112
        second_routing = 113113113
        new_bank_account = self.create_model(self.model, first_routing, 1)
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
            self.create_model(self.model, 'foo', 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 1234, 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 123456789, 'foo')

