import unittest

from . import RebaseModelTestCase
from rebase.models import Auction, Contractor, Nomination
from rebase.common.mock import create_one_nomination, create_one_contractor, create_one_auction

class TestNomination(RebaseModelTestCase):

    def test_create(self):
        nomination = create_one_nomination(self.db)
        self.db.session.commit()
        self.assertNotEqual( Nomination.query.get((nomination.contractor_id, nomination.ticket_set_id)), None )
        self.assertNotEqual( nomination,              None )
        self.assertNotEqual( nomination.contractor,   None )
        self.assertNotEqual( nomination.ticket_set,   None )
        self.assertEqual(    nomination.auction, None)

    def test_delete(self):
        nomination = create_one_nomination(self.db)
        self.db.session.commit()

        self.db.session.delete(nomination)
        self.db.session.commit()

        self.assertEqual(   Nomination.query.all(),    [] )
        self.assertNotEqual(Contractor.query.all(),     [] )
        self.assertNotEqual(Auction.query.all(),        [] )

    def test_delete_contractor(self):
        nomination = create_one_nomination(self.db)
        self.db.session.commit()

        self.db.session.delete(nomination.contractor)
        self.db.session.commit()

        self.assertEqual(   Nomination.query.all(),  [] )
        self.assertEqual(   Contractor.query.all(), [] )
        self.assertNotEqual(Auction.query.all(),    [] )

    def test_delete_auction(self):
        nomination = create_one_nomination(self.db)
        self.db.session.commit()

        self.db.session.delete(nomination.ticket_set.auction)
        self.db.session.commit()

        self.assertEqual(   Nomination.query.all(),    [] )
        self.assertNotEqual(Contractor.query.all(),     [] )
        self.assertEqual(   Auction.query.all(),        [] )

    def test_approve_talent(self):
        nomination = create_one_nomination(self.db)
        self.db.session.commit()

        nomination_id = (nomination.contractor_id, nomination.ticket_set_id)
        auction = nomination.ticket_set.auction
        auction.approved_talents.append(nomination)
        self.db.session.commit()

        self.assertEqual(nomination.auction.id, auction.id)

        # now disapprove talent
        auction.approved_talents.clear()
        self.db.session.add(auction)
        self.db.session.commit()
        queried_nomination = Nomination.query.get(nomination_id)
        self.assertTrue(queried_nomination)
        self.assertFalse(queried_nomination.auction)
        self.assertTrue(queried_nomination.ticket_set)

    def test_create_bad_ticket_set(self):
        contractor = create_one_contractor(self.db)
        with self.assertRaises(ValueError):
            nomination = Nomination(contractor, 'foobar')

    def test_create_bad_contractor(self):
        auction = create_one_auction(self.db)
        with self.assertRaises(ValueError):
            nomination = Nomination('foobar', auction)
