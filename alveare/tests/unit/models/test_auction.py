import unittest
import datetime

from sqlalchemy.exc import StatementError

from . import AlveareModelTestCase
from alveare.models import (
    Auction,
    Ticket,
    TicketSnapshot,
    TicketSet,
    BidLimit,
    TermSheet,
)

class TestAuctionModel(AlveareModelTestCase):

    def setUp(self):
        self.auctionArgs = {
            'ticket_prices':  [ (Ticket('Foo','Bar'), 111), (Ticket('Joe', 'Blow'), 222) ],
            'term_sheet':     TermSheet('yo mama shall not be so big'),
            'duration':       1000,
            'finish_work_by': datetime.datetime.today(),
            'redundancy':     1
        }
        super().setUp()

    def test_create(self):
        new_auction = self.create_model(Auction, **self.auctionArgs)

        for field in ['duration', 'finish_work_by', 'redundancy']:
            self.assertEqual( getattr(new_auction, field), self.auctionArgs[field] )

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
        
        new_auction = self.create_model(Auction, **self.auctionArgs)

        self.delete_instance(Auction, new_auction)

        self.assertEqual( TicketSet.query.all(),        [])
        self.assertEqual( BidLimit.query.all(),         [])
        self.assertEqual( TicketSnapshot.query.all(),   [])

        # verify that the original tickets have not been deleted
        for ticket, _ in self.auctionArgs['ticket_prices']:
            self.assertNotEqual(Ticket.query.get(ticket.id), None)

        # same for the term sheet
        self.assertNotEqual( TermSheet.query.get(self.auctionArgs['term_sheet'].id), None)

    def test_update(self):
        new_auction = self.create_model(Auction, **self.auctionArgs)

        tomorrows_date = self.auctionArgs['finish_work_by'] + datetime.timedelta(days=1)
        new_auction.duration = 4000
        new_auction.finish_work_by = tomorrows_date
        new_auction.redundancy = 2

        self.db.session.commit()

        modified_auction = Auction.query.get(new_auction.id)
        self.assertEqual(modified_auction.duration, 4000)
        self.assertEqual(modified_auction.finish_work_by, tomorrows_date)
        self.assertEqual(modified_auction.redundancy, 2)

    def test_bad_create(self):
        args = self.auctionArgs
        args['duration'] = 'foo'
        with self.assertRaises(ValueError):
            self.create_model(Auction, **args)
            
        args = self.auctionArgs
        args['finish_work_by'] = 'foo'
        with self.assertRaises(ValueError):
            self.create_model(Auction, **args)

        args = self.auctionArgs
        args['redundancy'] = 'foo'
        with self.assertRaises(ValueError):
            self.create_model(Auction, **args)
