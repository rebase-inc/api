from functools import partialmethod

from . import PermissionTestCase
from rebase.common.utils import ids, pick_a_word
from rebase.tests.common.ticket import (
    case_internal_contractor,
    case_internal_mgr,
    case_internal_admin,
    case_internal_admin_collection,
    case_internal_anonymous,
    case_internal_anonymous_collection,
)


def _new_instance(ticket):
    return {
        'project': ids(ticket.project),
        'title': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(5)),
        'description': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(15))
    }

class TestTicket(PermissionTestCase):
    model = 'InternalTicket'
    _create = partialmethod(PermissionTestCase.create, new_instance=_new_instance)

    def test_contractor_collection(self):
        self.collection(case_internal_contractor, 'contractor')

    def test_contractor_view(self):
        self.view(case_internal_contractor, 'contractor', True)

    def test_contractor_create(self):
        self._create(case_internal_contractor, 'contractor', False)

    def test_contractor_modify(self):
        self.modify(case_internal_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_internal_contractor, 'contractor', False)

    def test_mgr_collection(self):
        self.collection(case_internal_mgr, 'manager')

    def test_mgr_view(self):
        self.view(case_internal_mgr, 'manager', True)

    def test_mgr_create(self):
        self._create(case_internal_mgr, 'manager', True)

    def test_mgr_modify(self):
        self.modify(case_internal_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_internal_mgr, 'manager', True)

    def test_admin_collection(self):
        self.collection(case_internal_admin_collection, 'manager')

    def test_admin_view(self):
        self.view(case_internal_admin, 'manager', True)

    def test_admin_create(self):
        self._create(case_internal_admin, 'manager', True)

    def test_admin_modify(self):
        self.modify(case_internal_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_internal_admin, 'manager', True)

    def test_anonymous_view(self):
        self.view(case_internal_anonymous, 'manager', False)

    def test_anonymous_create(self):
        self._create(case_internal_anonymous, 'manager', False)

    def test_anonymous_modify(self):
        self.modify(case_internal_anonymous, 'manager', False)

    def test_anonymous_delete(self):
        self.delete(case_internal_anonymous, 'manager', False)

    def test_anonymous_collection(self):
        self.collection(case_internal_anonymous_collection, 'manager')
