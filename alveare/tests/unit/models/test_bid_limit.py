from . import AlveareModelTestCase
from datetime import datetime

from alveare import models

class TestBidLimitModel(AlveareModelTestCase):

    def setUp(self):
        self.ticket_0 = models.Ticket('Foo','Bar')
        self.ticket_1 = models.Ticket('Joe', 'Blow')
        self.ticket_2 = models.Ticket('Yo', 'Mama')
        self.auctionArgs = {
            'ticket_prices':  [ (self.ticket_0, 111), (self.ticket_1, 222) ],
            'term_sheet':     TermSheet('yo mama shall not be so big'),
            'duration':       1000,
            'finish_work_by': datetime.today(),
            'redundancy':     1
        }
        super().setUp()

    def test_create(self):
        bid_limit = self.create_bid_limit(10)
        self.assertEqual(bid_limit.price, 10)
        snapshot = models.TicketSnapshot.query.all()[0]
        self.assertNotEqual(snapshot, None)
        self.assertEqual(snapshot.ticket_id, bid_limit.snapshot.ticket.id)

    def test_delete(self):
        bid_limit = self.create_bid_limit(20)
        self.db.session.commit()
        self.delete_instance(models.BidLimit, bid_limit)
        self.assertEqual( models.BidLimit.query.all(), [] )

    def test_update(self):
        bid_limit = self.create_bid_limit(30)
        self.assertEqual(bid_limit.price, 30)
        self.db.session.commit()

        bid_limit.price = 40
        self.db.session.commit()

        modified_bid_limit = models.BidLimit.query.get(bid_limit.id)
        self.assertEqual(modified_bid_limit.price, 40)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_bid_limit(-10)
        with self.assertRaises(ValueError):
            self.create_bid_limit('foo')

