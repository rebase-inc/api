import unittest
import datetime

from sqlalchemy.exc import StatementError

from . import AlveareModelTestCase
from alveare import models

class TestAuctionModel(AlveareModelTestCase):
    model = models.Auction

    def test_create_auction(self):
        current_date = datetime.datetime.today()
        new_auction = self.create_model(self.model, 1000, current_date, 1)
        
        self.assertEqual(new_auction.duration, 1000)
        self.assertEqual(new_auction.finish_work_by, current_date)
        self.assertEqual(new_auction.redundancy, 1)

    def test_delete_auction(self):
        current_date = datetime.datetime.today()
        new_auction = self.create_model(self.model, 2000, current_date, 1)
        self.delete_instance(self.model, new_auction)

    def test_update_auction(self):
        current_date = datetime.datetime.today()
        new_auction = self.create_model(self.model, 3000, current_date, 1)
        
        self.assertEqual(new_auction.duration, 3000)
        self.assertEqual(new_auction.finish_work_by, current_date)
        self.assertEqual(new_auction.redundancy, 1)
       
        tomorrows_date = current_date + datetime.timedelta(days=1)
        new_auction.duration = 4000
        new_auction.finish_work_by = tomorrows_date 
        new_auction.redundancy = 2
        
        self.db.session.commit()
       
        modified_auction = self.model.query.get(new_auction.id)
        self.assertEqual(modified_auction.duration, 4000)
        self.assertEqual(modified_auction.finish_work_by, tomorrows_date)
        self.assertEqual(modified_auction.redundancy, 2)

    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo', datetime.datetime.today(), 1)
        with self.assertRaises(StatementError):
            self.create_model(self.model, 1, 'foo', 1)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 1, datetime.datetime.today(), 'foo')
