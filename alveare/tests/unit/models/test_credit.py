from . import AlveareModelTestCase

from alveare import models

class TestCreditModel(AlveareModelTestCase):
    model = models.Credit

    def test_create_credit(self):
        new_credit = self.create_model(self.model, 20)
        self.assertEqual(new_credit.price, 20)

    def test_delete_credit(self):
        new_credit = self.create_model(self.model, 30)
        self.assertEqual(new_credit.price, 30)
        self.delete_instance(self.model, new_credit)

    def test_update_credit(self):
        new_credit = self.create_model(self.model, 30)
        self.assertEqual(new_credit.price, 30)

        new_credit.price = 40
        self.db.session.commit()

        modified_credit = self.model.query.get(new_credit.id)
        self.assertEqual(modified_credit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo')

