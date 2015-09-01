from functools import partial

from . import PermissionTestCase
from rebase.common.utils import ids
from rebase.tests.common.ticket_set import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
)

def _new_instance(ticket_set):
    return {
        'bid_limits': [ ids(bid_limit) for bid_limit in ticket_set.bid_limits ]
    }

class TicketSetPermissions(PermissionTestCase):
    model = 'TicketSet'

    _create = partial(PermissionTestCase._create, new_instance=_new_instance)

    def test_mgr_collection(self):
        self.collection(case_mgr)

    def test_mgr_view(self):
        self.view(case_mgr, True)

    def test_mgr_modify(self):
        self.modify(case_mgr, True)

    def test_mgr_delete(self):
        self.delete(case_mgr, True)

    def test_mgr_create(self):
        TicketSetPermissions._create(self, case_mgr, True)

    def test_contractor_collection(self):
        self.collection(case_contractor)

    def test_contractor_view(self):
        self.view(case_contractor, True)

    def test_contractor_modify(self):
        self.modify(case_contractor, False)

    def test_contractor_delete(self):
        self.delete(case_contractor, False)

    def test_contractor_create(self):
        TicketSetPermissions._create(self, case_contractor, False)

    def test_admin_collection(self):
        self.collection(case_admin)

    def test_admin_view(self):
        self.view(case_admin, True)

    def test_admin_modify(self):
        self.modify(case_admin, True)

    def test_admin_delete(self):
        self.delete(case_admin, True)

    def test_admin_create(self):
        TicketSetPermissions._create(self, case_admin, True)
