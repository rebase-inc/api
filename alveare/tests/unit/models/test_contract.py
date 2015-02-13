import unittest
import datetime

from . import AlveareModelTestCase

from alveare.models import (
    TermSheet,
    Ticket,
    Bid,
    Auction,
    Contractor,
    Contract,
)

class TestContractModel(AlveareModelTestCase):
    def setUp(self):
        auctionArgs = {
            'ticket_prices':  [ (Ticket('Foo','Bar'), 111), (Ticket('Joe', 'Blow'), 222) ],
            'term_sheet':     TermSheet('yo mama shall not be so big'),
            'duration':       1000,
            'finish_work_by': datetime.datetime.today(),
            'redundancy':     1
        }

        self.auction = Auction(**auctionArgs)
        self.contractor = Contractor(1)
        self.bid = Bid(self.auction, self.contractor)
        super().setUp()

    def test_create(self):
        new_contract = self.create_model(Contract, self.bid)

    def test_delete(self):
        new_contract = self.create_model(Contract, self.bid)
        self.delete_instance(new_contract)

        self.assertNotEqual( Bid.query.get((self.auction.id, self.contractor.id)), None )

    @unittest.skip('Contract model doesnt have any updatable fields yet')
    def test_update(self):
        new_contract = self.create_model(self.model)

    @unittest.skip('Contract model doesnt have any creation fields yet')
    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo', 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 1234, 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 123456789, 'foo')

