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
from alveare.common import mock

class TestContractModel(AlveareModelTestCase):

    def test_create(self):
        bid = mock.create_one_bid(self.db)
        self.db.session.commit()

        new_contract = self.create_model(Contract, bid)
        self.assertEqual( new_contract.bid_id, bid.id )

    def test_delete(self):
        bid = mock.create_one_bid(self.db)
        self.db.session.commit()

        new_contract = self.create_model(Contract, bid)
        self.delete_instance(new_contract)
        self.assertNotEqual( Bid.query.get(bid.id), None )

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

