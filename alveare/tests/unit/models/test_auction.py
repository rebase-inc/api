import unittest
import datetime

from sqlalchemy.exc import StatementError

from . import AlveareModelTestCase
from alveare.models import Auction, Ticket, TicketSnapshot, TicketSet, BidLimit

class TestAuctionModel(AlveareModelTestCase):

    def setUp(self):
        self.ticket_prices = [ (Ticket('Foo','Bar'), 111), (Ticket('Joe', 'Blow'), 222) ]
        super().setUp()

    def test_create(self):
        current_date = datetime.datetime.today()
        new_auction = self.create_model(Auction, self.ticket_prices, 1000, current_date, 1)

        self.assertEqual(new_auction.duration, 1000)
        self.assertEqual(new_auction.finish_work_by, current_date)
        self.assertEqual(new_auction.redundancy, 1)
        self.assertNotEqual(new_auction.ticket_set, None)
        self.assertEqual(new_auction.ticket_set.auction_id, new_auction.id)
        self.assertEqual(len(new_auction.ticket_set.bid_limits), 2)
        self.assertEqual(new_auction.ticket_set.bid_limits[0].snapshot.ticket.title, 'Foo')
        self.assertEqual(new_auction.ticket_set.bid_limits[1].snapshot.ticket.title, 'Joe')

        snapshots = TicketSnapshot.query.all()
        self.assertEqual(snapshots[0].ticket.title, 'Foo')
        self.assertEqual(snapshots[1].ticket.title, 'Joe')

        tickets = Ticket.query.all()
        self.assertEqual(tickets[0].title, 'Foo')
        self.assertEqual(tickets[1].title, 'Joe')

    def test_delete(self):
        
        new_auction = self.create_model(Auction, self.ticket_prices, 2000, datetime.datetime.today(), 1)

        self.delete_instance(Auction, new_auction)

        self.assertEqual( TicketSet.query.all(),        [])
        self.assertEqual( BidLimit.query.all(),         [])
        self.assertEqual( TicketSnapshot.query.all(),   [])

    def test_update(self):
        current_date = datetime.datetime.today()
        new_auction = self.create_model(Auction, self.ticket_prices, 3000, current_date, 1)

        self.assertEqual(new_auction.duration, 3000)
        self.assertEqual(new_auction.finish_work_by, current_date)
        self.assertEqual(new_auction.redundancy, 1)

        tomorrows_date = current_date + datetime.timedelta(days=1)
        new_auction.duration = 4000
        new_auction.finish_work_by = tomorrows_date
        new_auction.redundancy = 2

        self.db.session.commit()

        modified_auction = Auction.query.get(new_auction.id)
        self.assertEqual(modified_auction.duration, 4000)
        self.assertEqual(modified_auction.finish_work_by, tomorrows_date)
        self.assertEqual(modified_auction.redundancy, 2)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(Auction, self.ticket_prices, 'foo', datetime.datetime.today(), 1)
        with self.assertRaises(StatementError):
            self.create_model(Auction, self.ticket_prices, 1, 'foo', 1)
        with self.assertRaises(ValueError):
            self.create_model(Auction, self.ticket_prices, 1, datetime.datetime.today(), 'foo')
