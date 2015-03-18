from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


# Note: there are no ticket creation tests here because only
# children classes of ticket have a valid constructor

class TestTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.ticket_resource = AlveareResource(self, 'Ticket')
        super().setUp()

    def test_get_one(self):
        ticket = self.ticket_resource.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertTrue(ticket['id'])
        self.assertTrue(ticket['skill_requirement'])
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])

    def test_update(self):
        ticket = self.ticket_resource.get_any()
        self.ticket_resource.update(
            id =            ticket['id'],
            title =         'Compelling title',
            description =   'Detailed description'
        )

    def test_delete(self):
        self.ticket_resource.delete_any()

    def test_delete_project(self):
        ticket = self.ticket_resource.get_any()
        self.delete_resource('projects/{id}'.format(**ticket['project']))
        self.get_resource(self.ticket_resource.url(ticket), 404)
