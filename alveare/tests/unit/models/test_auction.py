import copy
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


    auction_args = dict(
        tickets = [('Foo','Bar',111),('Joe','Blow',222)],
        terms = 'yo mama shall not be so big',
        duration = 1000,
        finish_by = datetime.datetime.today(),
        redundancy = 1
    )

    def test_create(self):
        auction = self.create_auction(**self.auction_args)
        self.db.session.commit()

        self.assertEqual(auction.duration, self.auction_args['duration'])
        self.assertEqual(auction.finish_work_by, self.auction_args['finish_by'])
        self.assertEqual(auction.redundancy, self.auction_args['redundancy'])

        self.assertNotEqual(auction.ticket_set, None)
        self.assertEqual(auction.ticket_set.auction_id, auction.id)
        self.assertEqual(len(auction.ticket_set.bid_limits), 2)
        self.assertEqual(auction.ticket_set.bid_limits[0].snapshot.ticket.title, 'Foo')
        self.assertEqual(auction.ticket_set.bid_limits[1].snapshot.ticket.title, 'Joe')

        snapshots = TicketSnapshot.query.all()
        self.assertEqual(snapshots[0].title, 'Foo')
        self.assertEqual(snapshots[1].title, 'Joe')

        tickets = Ticket.query.all()
        self.assertEqual(tickets[0].title, 'Foo')
        self.assertEqual(tickets[1].title, 'Joe')

    def test_delete(self):
        auction = self.create_auction(**self.auction_args)
        self.db.session.commit()

        tickets = [bl.snapshot.ticket for bl in auction.ticket_set.bid_limits]
        term_sheet = auction.term_sheet

        self.delete_instance(auction)

        self.assertEqual( TicketSet.query.all(),        [])
        self.assertEqual( BidLimit.query.all(),         [])
        self.assertEqual( TicketSnapshot.query.all(),   [])

        # verify that the original tickets have not been deleted
        for ticket in tickets:
            self.assertNotEqual(Ticket.query.get(ticket.id), None)

        # same for the term sheet
        self.assertNotEqual( TermSheet.query.get(term_sheet.id), None)

    def test_update(self):
        auction = self.create_auction(**self.auction_args)
        self.db.session.commit()

        tomorrows_date = self.auction_args['finish_by'] + datetime.timedelta(days=1)
        auction.duration = 4000
        auction.finish_work_by = tomorrows_date
        auction.redundancy = 2
        self.db.session.commit()

        modified_auction = Auction.query.get(auction.id)
        self.assertEqual(modified_auction.duration, 4000)
        self.assertEqual(modified_auction.finish_work_by, tomorrows_date)
        self.assertEqual(modified_auction.redundancy, 2)

    def test_bad_create(self):
        args = copy.copy(self.auction_args)
        args['duration'] = 'foo'
        with self.assertRaises(ValueError):
            self.create_auction(**args)

        args = copy.copy(self.auction_args)
        args['duration'] = 'foo'
        args['finish_by'] = 'foo'
        with self.assertRaises(ValueError):
            self.create_auction(**args)

        args = copy.copy(self.auction_args)
        args['redundancy'] = 'foo'
        with self.assertRaises(ValueError):
            self.create_auction(**args)
