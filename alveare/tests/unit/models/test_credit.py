from . import AlveareModelTestCase

from alveare import models

class TestCreditModel(AlveareModelTestCase):
    model = models.Credit

    def test_create(self):
        _, credit = self.create_debit_and_credit(10, 20)
        self.db.session.commit()

        self.assertEqual(credit.price, 20)

    def test_delete(self):
        _, credit = self.create_debit_and_credit(20, 30)
        self.db.session.commit()

        self.assertEqual(credit.price, 30)
        self.delete_instance(credit)
        self.assertEqual(models.Credit.query.get(credit.id), None)

    def test_update(self):
        _, credit = self.create_debit_and_credit(30, 40)
        self.db.session.commit()

        self.assertEqual(credit.price, 40)

        credit.price = 30
        self.db.session.commit()

        modified_credit = models.Credit.query.get(credit.id)
        self.assertEqual(modified_credit.price, 30)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            _, credit = self.create_debit_and_credit(40, 'foo')

