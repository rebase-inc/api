from . import AlveareModelTestCase
from datetime import datetime

from alveare import models
from alveare.common import mock

class TestBidLimitModel(AlveareModelTestCase):

    def test_create(self):
        bid_limit = mock.create_one_auction(self.db).ticket_set.bid_limits[0]
        self.db.session.commit()

        self.assertIsInstance(bid_limit.price, int)
        self.assertIsInstance(bid_limit.snapshot, models.TicketSnapshot)

    def test_delete(self):
        bid_limit = mock.create_one_auction(self.db).ticket_set.bid_limits[0]
        self.db.session.commit()

        self.delete_instance(bid_limit)
        self.assertEqual( models.BidLimit.query.get(bid_limit.id), None)

    def test_update(self):
        bid_limit = mock.create_one_auction(self.db).ticket_set.bid_limits[0]
        self.db.session.commit()
        old_price = bid_limit.price

        bid_limit.price = old_price + 10
        self.db.session.commit()

        modified_bid_limit = models.BidLimit.query.get(bid_limit.id)
        self.assertEqual(modified_bid_limit.price, old_price + 10)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            models.BidLimit(-10, 'bar')
        with self.assertRaises(ValueError):
            models.BidLimit('foo', 'bar')

