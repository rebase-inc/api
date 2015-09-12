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


class TestTicket(PermissionTestCase):
    model = 'InternalTicket'

    def new(_, ticket):
        return {
            'project': ids(ticket.project),
            'title': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(5)),
            'description': pick_a_word().capitalize()+' '.join(pick_a_word() for i in range(15))
        }

    def update(_, ticket):
        updated_ticket = ids(ticket)
        return updated_ticket

    def validateview(self, ticket):
        self.assertTrue(ticket)
        self.assertIn('id', ticket)
        self.assertIsInstance(ticket['id'], int)
        self.assertIn('title', ticket)
        self.assertIsInstance(ticket['title'], str)
        self.assertIn('description', ticket)
        self.assertIsInstance(ticket['description'], str)

    def test_contractor_collection(self):
        self.collection(case_internal_contractor, 'contractor')

    def test_contractorview(self):
        self.view(case_internal_contractor, 'contractor', True)

    def test_contractor_create(self):
        self.create(case_internal_contractor, 'contractor', False)

    def test_contractormodify(self):
        self.modify(case_internal_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_internal_contractor, 'contractor', False)

    def test_mgr_collection(self):
        self.collection(case_internal_mgr, 'manager')

    def test_mgrview(self):
        self.view(case_internal_mgr, 'manager', True)

    def test_mgr_create(self):
        self.create(case_internal_mgr, 'manager', True)

    def test_mgrmodify(self):
        self.modify(case_internal_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_internal_mgr, 'manager', True)

    def test_admin_collection(self):
        self.collection(case_internal_admin_collection, 'manager')

    def test_adminview(self):
        self.view(case_internal_admin, 'manager', True)

    def test_admin_create(self):
        self.create(case_internal_admin, 'manager', True)

    def test_adminmodify(self):
        self.modify(case_internal_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_internal_admin, 'manager', True)

    def test_anonymousview(self):
        self.view(case_internal_anonymous, 'manager', False)

    def test_anonymous_create(self):
        self.create(case_internal_anonymous, 'manager', False)

    def test_anonymousmodify(self):
        self.modify(case_internal_anonymous, 'manager', False)

    def test_anonymous_delete(self):
        self.delete(case_internal_anonymous, 'manager', False)

    def test_anonymous_collection(self):
        self.collection(case_internal_anonymous_collection, 'manager')
