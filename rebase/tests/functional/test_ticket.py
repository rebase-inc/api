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
        'title': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(5)),
        'description': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(15))
    }

class TestTicket(PermissionTestCase):
    model = 'InternalTicket'
    _create = partial(PermissionTestCase.create, new_instance=_new_instance)

    def test_contractor_view(self):
        self.view(case_contractor, 'contractor', True)

    def test_contractor_create(self):
        TestTicket._create(self, case_contractor, 'contractor', False)

    def test_contractor_modify(self):
        self.modify(case_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_contractor, 'contractor', False)

    def test_mgr_view(self):
        self.view(case_mgr, 'manager', True)

    def test_mgr_create(self):
        TestTicket._create(self, case_mgr, 'manager', True)

    def test_mgr_modify(self):
        self.modify(case_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_mgr, 'manager', True)

    def test_admin_view(self):
        self.view(case_admin, 'manager', True)

    def test_admin_create(self):
        TestTicket._create(self, case_admin, 'manager', True)

    def test_admin_modify(self):
        self.modify(case_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'manager', True)

    def test_anonymous_view(self):
        self.view(case_anonymous, 'manager', False)

    def test_anonymous_create(self):
        TestTicket._create(self, case_anonymous, 'manager', False)

    def test_anonymous_modify(self):
        self.modify(case_anonymous, 'manager', False)

    def test_anonymous_delete(self):
        self.delete(case_anonymous, 'manager', False)
