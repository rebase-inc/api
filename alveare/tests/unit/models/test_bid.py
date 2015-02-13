import unittest
import datetime

from . import AlveareModelTestCase

from alveare.models import (
    Bid,
    Auction,
    Contractor,
    Ticket,
    TermSheet
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
        new_bid = self.create_model(Bid, self.auction, self.contractor)

    def test_delete(self):
        new_bid = self.create_model(Bid, self.auction, self.contractor)
        self.delete_instance(Bid, new_bid)

        self.assertNotEqual( Auction.query.get(self.auction.id), None )
        self.assertNotEqual( Contractor.query.get(self.contractor.id), None )

    @unittest.skip('Bid model doesnt have any updatable fields yet')
    def test_update(self):
        new_bid = self.create_model(Bid, self.auction, self.contractor)

    @unittest.skip('Bid model doesnt have any creation fields yet')
    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(Bid, 'foo', self.contractor)
        with self.assertRaises(ValueError):
            self.create_model(Bid, self.auction, 2)

