from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


# Note: no creation tests, as RemoteTicket does not have a usable constructor.
# a child class must be used instead

class TestRemoteTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'remote_ticket')
        super().setUp()

    def test_get_one(self):
        ticket = self.r.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertTrue(ticket['id'])
        self.assertTrue(ticket['skill_requirement'])
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])

    # TODO: should fail, but read-only remote tickets are not implemented yet
    def test_update(self):
        ticket = self.r.get_any()
        ticket['title'] = 'Compelling title'
        ticket['description'] = 'Detailed description'
        self.r.update(**ticket) 

    def test_delete(self):
        self.r.delete_any()

    def test_delete_project(self):
        ticket = self.r.get_any()
        self.delete_resource('projects/{}'.format(ticket['project_id']))
        self.get_resource(self.r.url(ticket), 404)
