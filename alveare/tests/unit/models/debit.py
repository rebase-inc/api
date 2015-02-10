from . import AlveareTestCase

from alveare import models, create_app

class TestDebitModel(AlveareTestCase):

    def test_create_debit(self):
        self.db.session.add(models.Debit(20))
        self.db.session.commit()
        
        all_debits = models.Debit.query.all()
        self.assertEqual(len(all_debits), 1)
        
        new_debit = all_debits.pop()
        self.assertEqual(new_debit.price, 20)
