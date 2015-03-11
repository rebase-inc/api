import unittest

from . import AlveareRestTestCase

class TestAuctionResource(AlveareRestTestCase):

    @unittest.skip('this is just a stub')
    def test_get_all(self):
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)
        self.assertIsInstance(response['auctions'], list)
        self.assertIn('work_offers', response['bids'][0])
