from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


# Note: no creation tests, as RemoteTicket does not have a usable constructor.
# a child class must be used instead

class TestRemoteTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.remote_ticket_resource = AlveareResource(self, 'RemoteTicket')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        ticket = self.remote_ticket_resource.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertTrue(ticket['id'])
        self.assertTrue(ticket['skill_requirement'])
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])

    # TODO: should fail, but read-only remote tickets are not implemented yet
    def test_update(self):
        self.login_admin()
        ticket = self.remote_ticket_resource.get_any()
        ticket['title'] = 'Compelling title'
        ticket['description'] = 'Detailed description'
        self.remote_ticket_resource.update(**ticket) 

    def test_delete(self):
        self.login_admin()
        self.remote_ticket_resource.delete_any()

    def test_delete_project(self):
        self.login_admin()
        ticket = self.remote_ticket_resource.get_any()
        self.delete_resource('projects/{id}'.format(**ticket['project']))
        self.get_resource(self.remote_ticket_resource.url(ticket), 404)
