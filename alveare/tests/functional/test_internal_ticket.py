from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestInternalTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.internal_ticket_resource = AlveareResource(self, 'InternalTicket')
        super().setUp()

    def test_get_one(self):
        ticket = self.internal_ticket_resource.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertTrue(ticket['id'])
        self.assertTrue(ticket['skill_requirement'])
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])

    def test_create(self):
        project = AlveareResource(self, 'Project').get_any()
        self.internal_ticket_resource.create(title = 'Foo', description = 'Bar', project = dict(id=project['id']))

    def test_update(self):
        ticket = self.internal_ticket_resource.get_any()
        self.internal_ticket_resource.update(
            id =            ticket['id'],
            title =         'Compelling title',
            description =   'Detailed description'
        )

    def test_delete(self):
        self.internal_ticket_resource.delete_any()

    def test_delete_project(self):
        ticket = self.internal_ticket_resource.get_any()
        self.delete_resource('projects/{}'.format(ticket['project']['id']))
        self.get_resource(self.internal_ticket_resource.url(ticket), 404)
