import unittest

from . import AlveareModelTestCase
from alveare.models import Auction, Contractor, Feedback
from alveare.common.mock import create_one_feedback

class TestFeedbackModel(AlveareModelTestCase):

    def test_create(self):
        fb = create_one_feedback(self.db)
        self.db.session.commit()

        self.assertNotEqual( fb.contractor, None )
        self.assertNotEqual( fb.auction,    None )

    def test_delete(self):
        fb = create_one_feedback(self.db)
        self.db.session.commit()

        self.delete_instance(fb)

        self.assertNotEqual(Contractor.query.all(), [])
        self.assertNotEqual(Auction.query.all(), [])

    def test_delete_contractor(self):
        feedback = create_one_feedback(self.db)
        self.db.session.commit()

        auction = feedback.auction
        contractor = feedback.contractor

        self.db.session.delete(contractor)
        self.db.session.commit()

        self.assertEqual( Feedback.query.all(), [])
        self.assertEqual( auction.feedbacks, [] )

    def test_delete_auction(self):
        feedback = create_one_feedback(self.db)
        self.db.session.commit()

        auction = feedback.auction
        contractor = feedback.contractor

        self.db.session.delete(auction)
        self.db.session.commit()

        self.assertEqual( Feedback.query.all(), [])
        self.assertEqual( contractor.feedbacks, [] )

