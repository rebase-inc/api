import unittest

from . import AlveareModelTestCase
from alveare.models import Auction, Contractor, TalentMatch
from alveare.common.mock import create_one_talent_match, create_one_contractor, create_one_auction

class TestTalentMatchModel(AlveareModelTestCase):

    def test_create(self):
        score = 200
        talent_match = create_one_talent_match(self.db, score)
        self.db.session.commit()
        self.assertNotEqual( talent_match,              None )
        self.assertNotEqual( talent_match.contractor,   None )
        self.assertNotEqual( talent_match.ticket_set,   None )
        self.assertEqual(    talent_match.score,        score )
        self.assertEqual(    talent_match.approved_auction, None)

    def test_delete(self):
        talent_match = create_one_talent_match(self.db)
        self.db.session.commit()

        self.db.session.delete(talent_match)
        self.db.session.commit()

        self.assertEqual(   TalentMatch.query.all(),    [] )
        self.assertNotEqual(Contractor.query.all(),     [] )
        self.assertNotEqual(Auction.query.all(),        [] )

    def test_delete_contractor(self):
        talent_match = create_one_talent_match(self.db)
        self.db.session.commit()

        self.db.session.delete(talent_match.contractor)
        self.db.session.commit()

        self.assertEqual(   TalentMatch.query.all(),    [] )
        self.assertEqual(   Contractor.query.all(),     [] )
        self.assertNotEqual(Auction.query.all(),        [] )


    def test_delete_auction(self):
        talent_match = create_one_talent_match(self.db)
        self.db.session.commit()

        self.db.session.delete(talent_match.ticket_set.auction)
        self.db.session.commit()

        self.assertEqual(   TalentMatch.query.all(),    [] )
        self.assertNotEqual(Contractor.query.all(),     [] )
        self.assertEqual(   Auction.query.all(),        [] )

    def test_approve_talent(self):
        talent_match = create_one_talent_match(self.db)
        self.db.session.commit()

        auction = talent_match.ticket_set.auction
        auction.approved_talents.append(talent_match)
        self.db.session.commit()

        self.assertEqual(talent_match.approved_auction.id, auction.id)

        # now disapprove talent
        auction.approved_talents.clear()
        self.assertNotEqual(TalentMatch.query.all(), [])
        self.assertEqual(talent_match.approved_auction, None)

    def test_create_bad_ticket_set(self):
        contractor = create_one_contractor(self.db)
        talent_match = TalentMatch(contractor, 'foobar')
        with self.assertRaises(AttributeError):
            self.db.session.add(talent_match)

    def test_create_bad_contractor(self):
        auction = create_one_auction(self.db)
        talent_match = TalentMatch('foobar', auction)
        with self.assertRaises(AttributeError):
            self.db.session.add(talent_match)

