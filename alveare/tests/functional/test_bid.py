import unittest

from . import AlveareRestTestCase

class TestBidResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('bids')
        self.assertIn('bids', response)
        self.assertIsInstance(response['bids'], list)
        self.assertIn('work_offers', response['bids'][0])

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('bids')
        bid_id = response['bids'][0]['id']

        response = self.get_resource('bids/{}'.format(bid_id))
        bid = response['bid']

        self.assertEqual(bid.pop('id'), bid_id)
        self.assertIsInstance(bid.pop('work_offers'), list)
        self.assertIsInstance(bid.pop('contractor'), int)
        self.assertIsInstance(bid.pop('auction'), int)
        self.assertEqual(bid, {})

    def test_create_new(self):
        self.login_admin()
        ''' admin only '''
        user_data = dict(first_name='foo', last_name='bar', email='foo@bar.com', password='baz')
        user = self.post_resource('users', user_data)['user']
        contractor = self.post_resource('contractors', dict(user=user))['contractor']

        auction = self.get_resource('auctions')['auctions'][0]
        work_offer_ids = []
        for bid_limit in auction['ticket_set']['bid_limits']:
            snapshot_data = dict(ticket_snapshot = dict(id=bid_limit['ticket_snapshot']['id']), price=666, contractor=contractor)
            work_offer = self.post_resource('work_offers', snapshot_data)['work_offer']
            work_offer_ids.append(work_offer['id'])
        bid_data = dict(auction=auction, contractor=contractor)

        bid = self.post_resource('bids', bid_data)['bid']
        self.assertIsInstance(bid.pop('id'), int)
        self.assertEqual(bid.pop('auction'), auction['id'])
        self.assertEqual(bid.pop('contractor'), contractor['id'])
        self.assertEqual(bid.pop('work_offers'), work_offer_ids)
        self.assertEqual(bid, {})

    @unittest.skip('skipping this test for now')
    def test_update(self):
        self.login_admin()
        ''' admin only '''
        pass

