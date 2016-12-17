from math import floor

from . import RebaseRestTestCase, PermissionTestCase
from rebase.common.utils import ids
from rebase.models import Contractor, TicketSnapshot, WorkOffer
from rebase.tests.common.work_offer import (
    case_contractor,
    case_mgr,
    case_mgr_create,
    case_mgr_collection,
    case_admin,
)

class TestWorkOffer(PermissionTestCase):
    model = 'WorkOffer'

    def new(_, work_offer):
        return {
            'contractor':       ids(work_offer.contractor),
            'ticket_snapshot':  ids(work_offer.ticket_snapshot),
            'price':            floor(.9*work_offer.price)
        }

    def update(self, work_offer):
        new = self.new(work_offer)
        new.update(ids(work_offer))
        new['price'] = floor(new['price']*.7)
        return new

    def validate_view(test, work_offer):
        test.assertIsInstance(work_offer.pop('id'), int)
        test.assertIsInstance(work_offer.pop('work', 1), int)
        test.assertIsInstance(work_offer.pop('price'), int)
        snapshot = work_offer.pop('ticket_snapshot')
        test.assertIn('id', snapshot)
        test.assertIsInstance(work_offer.pop('contractor'), dict)
        test.assertEqual(work_offer, {})

    def test_mgr_delete(self):
        self.delete(case_mgr, 'manager', False)

    def test_mgr_collection(self):
        self.collection(case_mgr_collection, 'manager')

    def test_mgr_modify(self):
        self.modify(case_mgr, 'manager', False)

    def test_mgr_view(self):
        self.view(case_mgr, 'manager', True)

    def test_mgr_create(self):
        mgr_user, work_offer, snapshot_2 = case_mgr_create(self.db)
        self.create(lambda _: (mgr_user, work_offer), 'manager', False, delete_first=True)

    def test_contractor_delete(self):
        self.delete(case_contractor, 'contractor', True)

    def test_contractor_collection(self):
        self.collection(case_contractor, 'manager')

    def test_contractor_modify(self):
        self.modify(case_contractor, 'contractor', True)

    def test_contractor_view(self):
        self.view(case_contractor, 'contractor', True)

    def test_contractor_create(self):
        self.create(case_contractor, 'contractor', True, delete_first=True)
