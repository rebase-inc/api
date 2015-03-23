from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip

class TestTicketSetResource(AlveareRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'TicketSet')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        ticket_set = self.resource.get_any()
        self.assertTrue(ticket_set)
        self.assertTrue(ticket_set['id'])
        self.assertIsInstance(ticket_set['auction']['id'], int)
        self.assertIsInstance(ticket_set['bid_limits'], list)

    @skip('ticket set doesnt have any updatable fields')
    def test_update(self):
        self.login_admin()
        pass

    def test_delete(self):
        self.login_admin()
        self.resource.delete_any()

    def test_delete_auction(self):
        self.login_admin()
        ticket_set = self.resource.get_any()
        self.delete_resource('auctions/{id}'.format(**ticket_set['auction']))
        self.get_resource(self.resource.url(ticket_set), 404)
