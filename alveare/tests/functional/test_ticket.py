from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


# Note: there are no ticket creation tests here because only
# children classes of ticket have a valid constructor

class TestTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'ticket')
        super().setUp()

    def test_get_one(self):
        ticket = self.r.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertTrue(ticket['id'])
        self.assertTrue(ticket['skill_requirement'])
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])

    def test_update(self):
        ticket = self.r.get_any()
        self.r.update(
            id =            ticket['id'],
            title =         'Compelling title',
            description =   'Detailed description'
        )

    def test_delete(self):
        self.r.delete_any()

    def test_delete_project(self):
        ticket = self.r.get_any()
        self.delete_resource('projects/{}'.format(ticket['project_id']))
        self.get_resource(self.r.url(ticket), 404)
