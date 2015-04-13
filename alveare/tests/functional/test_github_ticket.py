from alveare.common.utils import AlveareResource
from unittest import skip
from .ticket import BaseTestTicketResource


class TestGithubTicketResource(BaseTestTicketResource):
    def setUp(self):
        super().setUp()
        self.ticket_resource = AlveareResource(self, 'GithubTicket')
        self.project_resource = AlveareResource(self, 'GithubProject')
        self.discriminator = 'github_ticket'
        self.check_discriminator = True
        self.allowed_project_types = ['github_project']

    def test_get_all_as_anonymous(self):
        self.get_all_as_anonymous()

    def test_get_all_as_admin(self):
        self.get_all_as_admin()

    def test_get_all_as_manager(self):
        self.get_all_as_manager()

    def test_get_all_as_contractor(self):
        self.get_all_as_contractor()

    def test_get_one_as_admin(self):
        self.get_one_as_admin()

    def test_get_one_as_manager(self):
        self.get_one_as_manager()

    def test_get_one_as_contractor(self):
        self.get_one_as_contractor()

    def test_get_invalid_id(self):
        self.get_invalid_id()

    def _create(self, expected_status=201):
        project = self.project_resource.get_any()
        self.assertTrue(project)
        self.ticket_resource.create(
            expected_status=expected_status,
            project = dict(id=project['id']),
            number = 13
        )

    def test_create_as_admin(self):
        self.create_as_admin()

    def test_create_as_manager(self):
        self.create_as_manager()

    def test_create_as_contractor(self):
        self.create_as_contractor()

    def test_update_as_admin(self):
        self.update_as_admin()

    def test_update_as_manager(self):
        self.update_as_manager()

    def test_update_as_contractor(self):
        self.update_as_contractor()

    def test_delete_as_admin(self):
        self.delete_as_admin()

    def test_delete_as_manager(self):
        self.delete_as_manager()

    def test_delete_as_contractor(self):
        self.delete_as_contractor()

    def test_delete_project(self):
        self.delete_project()
