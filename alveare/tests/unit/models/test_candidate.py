import unittest

from . import AlveareModelTestCase
from alveare.models import Auction, Contractor, Candidate
from alveare.common.mock import create_one_candidate, create_one_contractor, create_one_auction

class TestCandidate(AlveareModelTestCase):

    def test_create(self):
        candidate = create_one_candidate(self.db)
        self.db.session.commit()
        self.assertNotEqual( Candidate.query.get((candidate.contractor_id, candidate.auction_id)), None )
        self.assertNotEqual( candidate,              None )
        self.assertNotEqual( candidate.contractor,   None )
        self.assertNotEqual( candidate.ticket_set,   None )
        self.assertEqual(    candidate.approved_auction, None)

    def test_delete(self):
        candidate = create_one_candidate(self.db)
        self.db.session.commit()

        self.db.session.delete(candidate)
        self.db.session.commit()

        self.assertEqual(   Candidate.query.all(),    [] )
        self.assertNotEqual(Contractor.query.all(),     [] )
        self.assertNotEqual(Auction.query.all(),        [] )

    def test_delete_contractor(self):
        candidate = create_one_candidate(self.db)
        self.db.session.commit()

        self.db.session.delete(candidate.contractor)
        self.db.session.commit()

        self.assertEqual(   Candidate.query.all(),  [] )
        self.assertEqual(   Contractor.query.all(), [] )
        self.assertNotEqual(Auction.query.all(),    [] )

    def test_delete_auction(self):
        candidate = create_one_candidate(self.db)
        self.db.session.commit()

        self.db.session.delete(candidate.ticket_set.auction)
        self.db.session.commit()

        self.assertEqual(   Candidate.query.all(),    [] )
        self.assertNotEqual(Contractor.query.all(),     [] )
        self.assertEqual(   Auction.query.all(),        [] )

    def test_approve_talent(self):
        candidate = create_one_candidate(self.db)
        self.db.session.commit()

        candidate_id = (candidate.contractor_id, candidate.auction_id)
        auction = candidate.ticket_set.auction
        auction.approved_talents.append(candidate)
        self.db.session.commit()

        self.assertEqual(candidate.approved_auction.id, auction.id)

        # now disapprove talent
        auction.approved_talents.clear()
        self.db.session.add(auction)
        self.db.session.commit()
        self.assertTrue(Candidate.query.get(candidate_id))
        self.assertFalse(candidate.approved_auction)

    def test_create_bad_ticket_set(self):
        contractor = create_one_contractor(self.db)
        with self.assertRaises(AttributeError):
            candidate = Candidate(contractor, 'foobar')

    def test_create_bad_contractor(self):
        auction = create_one_auction(self.db)
        with self.assertRaises(AttributeError):
            candidate = Candidate('foobar', auction)
