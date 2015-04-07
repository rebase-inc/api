from .ticket import BaseTestTicketResource
from unittest import skip


# Note: there are no ticket creation tests here because only
# children classes of ticket have a valid constructor

class TestTicketResource(BaseTestTicketResource):
    def setUp(self):
        super().setUp()

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
