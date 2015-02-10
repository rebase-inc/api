from . import AlveareModelTestCase

from alveare import models

class TestBidLimitModel(AlveareModelTestCase):
    model = models.BidLimit

    def test_create(self):
        new_bank_account = self.create_model(self.model, 10)
        self.assertEqual(new_bank_account.price, 10)

    def test_delete(self):
        new_bank_account = self.create_model(self.model, 20)
        self.delete_instance(self.model, new_bank_account)

    def test_update(self):
        new_bank_account = self.create_model(self.model, 30)
        self.assertEqual(new_bank_account.price, 30)

        new_bank_account.price = 40
        self.db.session.commit()

        modified_bank_account = self.model.query.get(new_bank_account.id)
        self.assertEqual(modified_bank_account.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, -10)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo')

