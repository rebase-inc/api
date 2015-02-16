import unittest

from . import AlveareModelTestCase
from alveare.models import Auction, Contractor, TalentMatch
from alveare.common.mock import create_one_talent_match

class TestTalentMatchModel(AlveareModelTestCase):

    def test_create(self):
        score = 200
        talent_match = create_one_talent_match(self.db, score)
        self.db.session.commit()
        self.assertNotEqual( talent_match,              None )
        self.assertNotEqual( talent_match.contractor,   None )
        self.assertNotEqual( talent_match.ticket_set,   None )
        self.assertEqual(    talent_match.score,        score )

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
