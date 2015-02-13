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
        bid = self.create_bid([('foo','bar',100),('baz','qux',200)])
        self.db.session.commit()

        found_bid = Bid.query.get((self.auction.id, self.contractor.id))
        self.assertEqual(len(found_bid.work_offers.all()), 2)
        self.assertEqual(found_bid.work_offers.all()[0].ticket_snapshot.title, 'foo')
        self.assertEqual(found_bid.work_offers.all()[1].ticket_snapshot.title, 'baz')


    def test_delete(self):
        bid = self.create_bid([('foo','bar',100),('baz','qux',200)])
        self.db.session.commit()

        work_offer_id1 = bid.work_offers.all()[0].id
        work_offer_id2 = bid.work_offers.all()[1].id

        self.delete_instance(models.Bid, bid)

        self.assertEqual(Bid.query.get((self.auction.id, self.contractor.id)), None)
        self.assertNotEqual( Auction.query.get(self.auction.id), None )
        self.assertNotEqual( Contractor.query.get(self.contractor.id), None )

        self.assertEqual(models.WorkOffer.query.get(work_offer_id1), None)
        self.assertEqual(models.WorkOffer.query.get(work_offer_id2), None)

    #@unittest.skip('Bid model doesnt have any updatable fields yet')
    #def test_update(self):
        #return

    #@unittest.skip('Bid model doesnt have any creation fields yet')
    #def test_bad_create(self):
        #return

