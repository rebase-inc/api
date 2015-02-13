from . import AlveareModelTestCase

from alveare import models
from alveare.common import mock

class TestDebitModel(AlveareModelTestCase):

    def test_create(self):
        work = mock.create_some_work(self.db).pop()
        debit = work.debit
        self.db.session.commit()

        self.assertIsInstance(debit.price, int)

    def test_delete(self):
        work = mock.create_some_work(self.db).pop()
        debit = work.debit
        self.db.session.commit()

        self.assertIsInstance(debit.price, int)
        self.delete_instance(models.Debit, debit)
        self.assertEqual(models.Debit.query.get(debit.id), None)

    def test_update(self):
        work = mock.create_some_work(self.db).pop()
        debit = work.debit
        self.db.session.commit()

        self.assertIsInstance(debit.price, int)

        debit.price = 40
        self.db.session.commit()

        modified_debit = models.Debit.query.get(debit.id)
        self.assertEqual(modified_debit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(models.Debit, 'foo', 'foo')

