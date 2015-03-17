from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip

class TestBidLimitResource(AlveareRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'bid_limit')
        super().setUp()

    def test_get_one(self):
        bid_limit = self.resource.get_any()
        self.assertTrue(bid_limit)
        self.assertTrue(bid_limit.pop('id'))
        self.assertIsInstance(bid_limit.pop('price'), int)
        self.assertIsInstance(bid_limit.pop('ticket_set').pop('id'), int)
        self.assertIsInstance(bid_limit.pop('ticket_snapshot').pop('id'), int)
        self.assertEqual(bid_limit, {})

    @skip('ticket set doesnt have any updatable fields')
    def test_update(self):
        pass

    def test_delete(self):
        self.resource.delete_any()

    def test_delete_auction(self):
        bid_limit = self.resource.get_any()
        self.delete_resource('ticket_sets/{}'.format(bid_limit['ticket_set']['id']))
        self.get_resource(self.resource.url(bid_limit), 404)
