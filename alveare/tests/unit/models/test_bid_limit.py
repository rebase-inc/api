from . import AlveareModelTestCase

from alveare import models

class TestBidLimitModel(AlveareModelTestCase):
    model = models.BidLimit

    def test_create(self):
        new_bid_limit = self.create_model(self.model, 10)
        self.assertEqual(new_bid_limit.price, 10)

    def test_delete(self):
        new_bid_limit = self.create_model(self.model, 20)
        self.delete_instance(self.model, new_bid_limit)

    def test_update(self):
        new_bid_limit = self.create_model(self.model, 30)
        self.assertEqual(new_bid_limit.price, 30)

        new_bid_limit.price = 40
        self.db.session.commit()

        modified_bid_limit = self.model.query.get(new_bid_limit.id)
        self.assertEqual(modified_bid_limit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, -10)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo')

