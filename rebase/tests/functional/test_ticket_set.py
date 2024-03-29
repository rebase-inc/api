from . import PermissionTestCase
from rebase.common.utils import ids
from rebase.tests.common.ticket_set import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
)

class TicketSetPermissions(PermissionTestCase):
    model = 'TicketSet'

    def new(self, ticket_set):
        return {
            'bid_limits': [ ids(bid_limit) for bid_limit in ticket_set.bid_limits ]
        }

    def update(self, ticket_set):
        updated_ticket_set = ids(ticket_set)
        return updated_ticket_set

    def validate_view(self, ticket_set):
        self.assertIn('bid_limits', ticket_set)
        self.assertIsInstance(ticket_set['bid_limits'], list)

    def test_mgr_collection(self):
        self.collection(case_mgr, 'manager')

    def test_mgr_view(self):
        self.view(case_mgr, 'manager', True)

    def test_mgr_modify(self):
        self.modify(case_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_mgr, 'manager', True)

    def test_mgr_create(self):
        self.create(case_mgr, 'manager', True)

    def test_contractor_collection(self):
        self.collection(case_contractor, 'contractor')

    def test_contractor_view(self):
        self.view(case_contractor, 'contractor', True)

    def test_contractor_modify(self):
        self.modify(case_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_contractor, 'contractor', False)

    def test_contractor_create(self):
        self.create(case_contractor, 'contractor', False)

    def test_admin_collection(self):
        self.collection(case_admin, 'manager')

    def test_admin_view(self):
        self.view(case_admin, 'manager', True)

    def test_admin_modify(self):
        self.modify(case_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'manager', True)

    def test_admin_create(self):
        self.create(case_admin, 'manager', True)
