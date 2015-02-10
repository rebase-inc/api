from . import AlveareModelTestCase

from alveare import models

class TestDebitModel(AlveareModelTestCase):
    model = models.Debit

    def test_create(self):
        new_debit = self.create_model(self.model, 20)
        self.assertEqual(new_debit.price, 20)

    def test_delete(self):
        new_debit = self.create_model(self.model, 30)
        self.assertEqual(new_debit.price, 30)
        self.delete_instance(self.model, new_debit)

    def test_update(self):
        new_debit = self.create_model(self.model, 30)
        self.assertEqual(new_debit.price, 30)

        new_debit.price = 40
        self.db.session.commit()

        modified_debit = self.model.query.get(new_debit.id)
        self.assertEqual(modified_debit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo')

