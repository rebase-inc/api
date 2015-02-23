import unittest

from . import AlveareModelTestCase
from alveare.models import Auction, Contractor, Candidate
from alveare.common.mock import create_one_candidate, create_one_contractor, create_one_auction

class TestCandidateModel(AlveareModelTestCase):

    def test_create(self):
        candidate = create_one_candidate(self.db)
        self.db.session.commit()
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

        auction = candidate.ticket_set.auction
        auction.approved_talents.append(candidate)
        self.db.session.commit()

        self.assertEqual(candidate.approved_auction.id, auction.id)

        # now disapprove talent
        auction.approved_talents.clear()
        self.assertNotEqual(Candidate.query.all(), [])
        self.assertEqual(candidate.approved_auction, None)

    def test_create_bad_ticket_set(self):
        contractor = create_one_contractor(self.db)
        with self.assertRaises(AttributeError):
            candidate = Candidate(contractor, 'foobar')

    def test_create_bad_contractor(self):
        auction = create_one_auction(self.db)
        with self.assertRaises(AttributeError):
            candidate = Candidate('foobar', auction)
