from . import RebaseRestTestCase
from rebase.common.utils import RebaseResource
from unittest import skip

class TestBidLimitResource(RebaseRestTestCase):
    def setUp(self):
        self.resource = RebaseResource(self, 'BidLimit')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        bid_limit = self.resource.get_any()
        self.assertTrue(bid_limit)
        self.assertTrue(bid_limit.pop('id'))
        self.assertIsInstance(bid_limit.pop('price'), int)
        self.assertIsInstance(bid_limit.pop('ticket_set').pop('id'), int)
        self.assertIsInstance(bid_limit.pop('ticket_snapshot').pop('id'), int)
        self.assertEqual(bid_limit, {})

    @skip('ticket set doesnt have any updatable fields')
    def test_update(self):
        self.login_admin()
        pass

    def test_delete(self):
        self.login_admin()
        self.resource.delete_any()

    def test_delete_auction(self):
        self.login_admin()
        bid_limit = self.resource.get_any()
        self.delete_resource('ticket_sets/{}'.format(bid_limit['ticket_set']['id']))
        self.get_resource(self.resource.url(bid_limit), 404)
