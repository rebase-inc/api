import unittest

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare import models

class TestBidModel(AlveareModelTestCase):

    def test_create(self):
        bid = self.create_bid([('foo','bar',100),('baz','qux',200)])
        self.db.session.commit()

        found_bid = models.Bid.query.get(bid.id)
        self.assertEqual(len(found_bid.work_offers.all()), 2)
        self.assertEqual(found_bid.work_offers.all()[0].ticket_snapshot.title, 'foo')
        self.assertEqual(found_bid.work_offers.all()[1].ticket_snapshot.title, 'baz')


    def test_delete(self):
        bid = self.create_bid([('foo','bar',100),('baz','qux',200)])
        self.db.session.commit()

        work_offer_id1 = bid.work_offers.all()[0].id
        work_offer_id2 = bid.work_offers.all()[1].id

        self.delete_instance(models.Bid, bid)

        self.assertEqual(models.Bid.query.get(bid.id), None)

        self.assertEqual(models.WorkOffer.query.get(work_offer_id1), None)
        self.assertEqual(models.WorkOffer.query.get(work_offer_id2), None)

    @unittest.skip('Bid model doesnt have any updatable fields yet')
    def test_update(self):
        return

    @unittest.skip('Bid model doesnt have any creation fields yet')
    def test_bad_create(self):
        return

