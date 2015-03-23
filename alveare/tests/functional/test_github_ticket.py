from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestGithubTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.github_ticket_resource = AlveareResource(self, 'GithubTicket')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        ticket = self.github_ticket_resource.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertTrue(ticket['id'])
        self.assertTrue(ticket['skill_requirement'])
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])

    def test_create(self):
        self.login_admin()
        ticket = self.github_ticket_resource.get_any()
        self.github_ticket_resource.create(project = ticket['project'], number = 1234)

    # TODO: should fail, but read-only remote tickets are not implemented yet
    def test_update(self):
        self.login_admin()
        ticket = self.github_ticket_resource.get_any()
        ticket['title'] = 'Compelling title'
        ticket['description'] = 'Detailed description'
        self.github_ticket_resource.update(**ticket) 

    def test_delete(self):
        self.login_admin()
        self.github_ticket_resource.delete_any()

    def test_delete_project(self):
        self.login_admin()
        ticket = self.github_ticket_resource.get_any()
        self.delete_resource('projects/{id}'.format(**ticket['project']))
        self.get_resource(self.github_ticket_resource.url(ticket), 404)
