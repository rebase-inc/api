from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestCreditModel(AlveareModelTestCase):

    def test_create(self):
        work = mock.create_some_work(self.db).pop()
        credit = work.credit
        self.db.session.commit()

        self.assertIsInstance(credit.price, int)

    def test_delete(self):
        work = mock.create_some_work(self.db).pop()
        credit = work.credit
        self.db.session.commit()

        self.assertIsInstance(credit.price, int)
        self.delete_instance(models.Credit, credit)
        self.assertEqual(models.Credit.query.get(credit.id), None)

    def test_update(self):
        work = mock.create_some_work(self.db).pop()
        credit = work.credit
        self.db.session.commit()

        self.assertIsInstance(credit.price, int)

        credit.price = 40
        self.db.session.commit()

        modified_credit = models.Credit.query.get(credit.id)
        self.assertEqual(modified_credit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Credit, 'foo', 'foo')

