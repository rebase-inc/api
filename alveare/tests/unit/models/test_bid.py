import unittest

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models

class TestBidModel(AlveareModelTestCase):

    def test_create(self):
        ts1 = self.create_model(models.TicketSnapshot, models.Ticket('foo', 'bar'))
        ts2 = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer1 = models.WorkOffer(bid, ts1, 100)
        work_offer2 = models.WorkOffer(bid, ts2, 200)
        self.db.session.add(bid)
        self.db.session.add(work_offer1)
        self.db.session.add(work_offer2)
        self.db.session.commit()

        found_bid = models.Bid.query.get(bid.id)
        self.assertEqual(len(found_bid.work_offers.all()), 2)
        self.assertIn(found_bid.work_offers.all()[0].ticket_snapshot.title, ['foo', 'baz'])
        self.assertIn(found_bid.work_offers.all()[1].ticket_snapshot.title, ['foo', 'baz'])


    def test_delete(self):
        ts1 = self.create_model(models.TicketSnapshot, models.Ticket('foo', 'bar'))
        ts2 = self.create_model(models.TicketSnapshot, models.Ticket('baz', 'qux'))
        bid = models.Bid()
        work_offer1 = models.WorkOffer(bid, ts1, 100)
        work_offer2 = models.WorkOffer(bid, ts2, 200)
        self.db.session.add(bid)
        self.db.session.add(work_offer1)
        self.db.session.add(work_offer2)
        self.db.session.commit()

        self.delete_instance(models.Bid, bid)

        self.assertEqual(models.Bid.query.get(bid.id), None)

        with self.assertRaises(ObjectDeletedError):
            models.WorkOffer.query.get(work_offer1.id)
        with self.assertRaises(ObjectDeletedError):
            models.WorkOffer.query.get(work_offer2.id)

    @unittest.skip('Bid model doesnt have any updatable fields yet')
    def test_update(self):
        return

    @unittest.skip('Bid model doesnt have any creation fields yet')
    def test_bad_create(self):
        return

