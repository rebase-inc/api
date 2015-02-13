import unittest
import datetime

from sqlalchemy.orm.exc import ObjectDeletedError

from . import AlveareModelTestCase

from alveare.models import (
    Bid,
    Auction,
    Contractor,
    Ticket,
    TicketSnapshot,
    TermSheet,
    WorkOffer,
)

class TestBidModel(AlveareModelTestCase):

    def setUp(self):

        self.auctionArgs = {
            'ticket_prices':  [ (Ticket('Foo','Bar'), 111), (Ticket('Joe', 'Blow'), 222) ],
            'term_sheet':     TermSheet('yo mama shall not be so big'),
            'duration':       1000,
            'finish_work_by': datetime.datetime.today(),
            'redundancy':     1
        }

        self.auction = Auction(**self.auctionArgs)
        self.contractor = Contractor(1)
        super().setUp()

    def test_create(self):
        bid = Bid(self.auction, self.contractor)
        ts1 = self.auction.ticket_set.bid_limits[0].snapshot
        ts2 = self.auction.ticket_set.bid_limits[1].snapshot
        work_offer1 = WorkOffer(bid, ts1, 100)
        work_offer2 = WorkOffer(bid, ts2, 200)
        self.db.session.add(bid)
        self.db.session.commit()

        found_bid = Bid.query.get((self.auction.id, self.contractor.id))
        self.assertEqual(len(found_bid.work_offers.all()), 2)
        self.assertIn(found_bid.work_offers.all()[0].ticket_snapshot.title, ['Foo', 'Bar'])
        self.assertIn(found_bid.work_offers.all()[1].ticket_snapshot.title, ['Joe', 'Blow'])

    def test_delete(self):
        bid = Bid(self.auction, self.contractor)

        ts1 = self.auction.ticket_set.bid_limits[0].snapshot
        ts2 = self.auction.ticket_set.bid_limits[1].snapshot
        work_offer1 = WorkOffer(bid, ts1, 100)
        work_offer2 = WorkOffer(bid, ts2, 200)

        self.db.session.add(bid)
        self.db.session.commit()

        self.db.session.delete(work_offer1)
        self.db.session.delete(work_offer2)
        self.db.session.delete(bid)
        self.db.session.commit()

        self.assertEqual(Bid.query.get((self.auction.id, self.contractor.id)), None)
        self.assertNotEqual( Auction.query.get(self.auction.id), None )
        self.assertNotEqual( Contractor.query.get(self.contractor.id), None )

        #with self.assertRaises(ObjectDeletedError):
            #WorkOffer.query.get(work_offer1.id)
        #with self.assertRaises(ObjectDeletedError):
            #WorkOffer.query.get(work_offer2.id)

    #@unittest.skip('Bid model doesnt have any updatable fields yet')
    #def test_update(self):
        #return

    #@unittest.skip('Bid model doesnt have any creation fields yet')
    #def test_bad_create(self):
        #return

