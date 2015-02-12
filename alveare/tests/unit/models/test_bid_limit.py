from . import AlveareModelTestCase

from alveare.models import BidLimit, Ticket, TicketSnapshot

class TestBidLimitModel(AlveareModelTestCase):

    def test_create(self):
        ticket = Ticket('Foo','Bar')
        new_bid_limit = self.create_model(BidLimit, ticket, 10)

        self.assertEqual(new_bid_limit.price, 10)
        snapshot = TicketSnapshot.query.all()[0]
        self.assertNotEqual(snapshot, None)
        self.assertEqual(snapshot.ticket_id, ticket.id)

    def test_delete(self):
        new_bid_limit = self.create_model(BidLimit, Ticket('Foo','Bar'), 20)
        self.delete_instance(BidLimit, new_bid_limit)

        self.assertEqual( BidLimit.query.all(), [] )

    def test_update(self):
        new_bid_limit = self.create_model(BidLimit, Ticket('Foo','Bar'), 30)
        self.assertEqual(new_bid_limit.price, 30)

        new_bid_limit.price = 40
        self.db.session.commit()

        modified_bid_limit = BidLimit.query.get(new_bid_limit.id)
        self.assertEqual(modified_bid_limit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(BidLimit, Ticket('Foo','Bar'), -10)
        with self.assertRaises(ValueError):
            self.create_model(BidLimit, Ticket('Foo','Bar'), 'foo')

