import copy
import unittest
import datetime

from sqlalchemy.exc import StatementError

from . import AlveareModelTestCase
from alveare.models import Auction, Ticket, TicketSnapshot, TicketSet, BidLimit, TermSheet
from alveare import models
from alveare.common import mock

class TestAuctionModel(AlveareModelTestCase):

    def test_create(self):
        auction = mock.create_one_auction(self.db)
        self.db.session.commit()

        self.assertIsInstance(auction.duration, int)
        self.assertIsInstance(auction.finish_work_by, datetime.datetime)
        self.assertIsInstance(auction.redundancy, int)

        self.assertIsInstance(auction.ticket_set, models.TicketSet)
        self.assertEqual(auction.ticket_set.auction_id, auction.id)
        self.assertIsInstance(auction.ticket_set.bid_limits.pop(), models.BidLimit)
        self.assertIsInstance(auction.ticket_set.bid_limits[0].snapshot.ticket.title, str)

    def test_delete(self):
        auction = mock.create_one_auction(self.db)
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
        auction = mock.create_one_auction(self.db)
        self.db.session.commit()

        tomorrows_date = datetime.datetime.now() + datetime.timedelta(days=1)
        auction.duration = 4000
        auction.finish_work_by = tomorrows_date
        auction.redundancy = 2
        self.db.session.commit()

        modified_auction = Auction.query.get(auction.id)
        self.assertEqual(modified_auction.duration, 4000)
        self.assertEqual(modified_auction.finish_work_by, tomorrows_date)
        self.assertEqual(modified_auction.redundancy, 2)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            auction = mock.create_one_auction(self.db, duration='foo')
            self.db.session.commit()

        with self.assertRaises(ValueError):
            auction = mock.create_one_auction(self.db, finish_work_by='foo')
            self.db.session.commit()

        with self.assertRaises(ValueError):
            auction = mock.create_one_auction(self.db, redundancy='foo')
            self.db.session.commit()
