from . import AlveareModelTestCase
from datetime import datetime

from alveare.models import (
    Auction,
    BidLimit,
    Ticket,
    TicketSnapshot,
    TermSheet,
)

class TestBidLimitModel(AlveareModelTestCase):

    def setUp(self):
        self.ticket_0 = Ticket('Foo','Bar')
        self.ticket_1 = Ticket('Joe', 'Blow')
        self.ticket_2 = Ticket('Yo', 'Mama')
        self.auctionArgs = {
            'ticket_prices':  [ (self.ticket_0, 111), (self.ticket_1, 222) ],
            'term_sheet':     TermSheet('yo mama shall not be so big'),
            'duration':       1000,
            'finish_work_by': datetime.today(),
            'redundancy':     1
        }
        super().setUp()

    def test_create(self):
        auction = self.create_model(Auction, **self.auctionArgs)

        self.assertEqual( len(auction.ticket_set.bid_limits), 2)
        bid_limit_0 = auction.ticket_set.bid_limits[0]
        bid_limit_1 = auction.ticket_set.bid_limits[1]

        self.assertEqual(bid_limit_0.price, 111)
        self.assertEqual(bid_limit_1.price, 222)
        snapshot = TicketSnapshot.query.all()[0]
        self.assertNotEqual(snapshot, None)
        self.assertEqual(snapshot.ticket_id, self.ticket_0.id)

    def test_delete(self):
        auction = self.create_model(Auction, **self.auctionArgs)

        bid_limits = BidLimit.query.all()
        self.assertEqual( len(bid_limits), 2)

        self.delete_instance(BidLimit, bid_limits[0])
        self.delete_instance(BidLimit, bid_limits[1])

        self.assertEqual( BidLimit.query.all(), [] )
        self.assertEqual( TicketSnapshot.query.all(), [] )

    def test_update(self):
        auction = self.create_model(Auction, **self.auctionArgs)

        bid_limits = BidLimit.query.all()
        self.assertEqual( len(bid_limits), 2)

        bid_limits[0].price = 40
        self.db.session.add(bid_limits[0])
        self.db.session.commit()

        modified_bid_limit = BidLimit.query.get(bid_limits[0].id)
        self.assertEqual(modified_bid_limit.price, 40)

    def test_bad_create(self):
        auction = self.create_model(Auction, **self.auctionArgs)
        with self.assertRaises(ValueError):
            auction.ticket_set.add(self.ticket_2, -10)
        with self.assertRaises(ValueError):
            auction.ticket_set.add(self.ticket_2, 'foo')

