from . import AlveareModelTestCase

from alveare import models

class TestDebitModel(AlveareModelTestCase):

    def test_create(self):
        debit, _ = self.create_debit_and_credit(10, 20)
        self.db.session.commit()

        self.assertEqual(debit.price, 10)

    def test_delete(self):
        debit, _ = self.create_debit_and_credit(20, 30)
        self.db.session.commit()

        self.assertEqual(debit.price, 20)
        self.delete_instance(debit)
        self.assertEqual(models.Debit.query.get(debit.id), None)

    def test_update(self):
        debit, _ = self.create_debit_and_credit(30, 40)
        self.db.session.commit()

        self.assertEqual(debit.price, 30)

        debit.price = 40
        self.db.session.commit()

        modified_debit = models.Debit.query.get(debit.id)
        self.assertEqual(modified_debit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            debit, _ = self.create_debit_and_credit('foo', 40)

