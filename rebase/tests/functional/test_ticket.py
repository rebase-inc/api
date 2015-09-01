from functools import partial
from unittest import skip

from . import PermissionTestCase
from rebase.common.utils import ids, pick_a_word
from rebase.tests.common.ticket import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
)
from .ticket import BaseTestTicketResource


def _new_instance(ticket):
    return {
        'project': ids(ticket.project),
        'title': pick_a_word().capitalize().join(pick_a_word() for i in range(5)),
        'description': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(15))
    }

class TestTicket(PermissionTestCase):
    model = 'InternalTicket'
    _create = partial(PermissionTestCase.create, new_instance=_new_instance)

    def test_contractor_view(self):
        self.view(case_contractor, True)

    def test_contractor_create(self):
        TestTicket._create(self, case_contractor, False)

    def test_contractor_modify(self):
        self.modify(case_contractor, False)

    def test_contractor_delete(self):
        self.delete(case_contractor, False)

    def test_mgr_view(self):
        self.view(case_mgr, True)

    def test_mgr_create(self):
        TestTicket._create(self, case_mgr, True)

    def test_mgr_modify(self):
        self.modify(case_mgr, True)

    def test_mgr_delete(self):
        self.delete(case_mgr, True)

    def test_admin_view(self):
        self.view(case_admin, True)

    def test_admin_create(self):
        TestTicket._create(self, case_admin, True)

    def test_admin_modify(self):
        self.modify(case_admin, True)

    def test_admin_delete(self):
        self.delete(case_admin, True)

    def test_anonymous_view(self):
        self.view(case_anonymous, False)

    def test_anonymous_create(self):
        TestTicket._create(self, case_anonymous, False)

    def test_anonymous_modify(self):
        self.modify(case_anonymous, False)

    def test_anonymous_delete(self):
        self.delete(case_anonymous, False)



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
