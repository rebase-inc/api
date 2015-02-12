from . import AlveareModelTestCase

from alveare import models

class TestDebitModel(AlveareModelTestCase):
    model = models.Debit

    def test_create(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        new_debit = self.create_model(self.model, work, 10)
        self.assertEqual(new_debit.price, 10)

    def test_delete(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        new_debit = self.create_model(self.model, work, 20)
        self.assertEqual(new_debit.price, 20)
        self.delete_instance(self.model, new_debit)

    def test_update(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        new_debit = self.create_model(self.model, work, 30)
        self.assertEqual(new_debit.price, 30)

        new_debit.price = 40
        self.db.session.commit()

        modified_debit = self.model.query.get(new_debit.id)
        self.assertEqual(modified_debit.price, 40)

    def test_bad_create(self):
        ticket_snap = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer = models.WorkOffer(bid, ticket_snap, 100)
        work = self.create_model(models.Work, work_offer)
        with self.assertRaises(ValueError):
            self.create_model(self.model, work, 'foo')

