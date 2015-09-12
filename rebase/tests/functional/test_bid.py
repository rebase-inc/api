from functools import partialmethod

from . import PermissionTestCase

from rebase.models import Bid, Contractor, Manager
from rebase.common.utils import ids
from rebase.tests.common.bid import case_mgr, case_contractor, case_admin


class TestBid(PermissionTestCase):
    model = 'Bid'

    def new(self, instance):
        return {
            'auction': ids(instance.auction),
            'contractor': ids(instance.contractor),
            'work_offers': [ ids(wo) for wo in instance.work_offers.all() ]
        }

    def update(self, bid):
        updated_bid = ids(bid)
        return updated_bid

    def validate_view(self, bid):
        self.assertTrue(bid)
        self.assertIn('contractor', bid)
        self.assertIsInstance(bid['contractor'], int)
        self.assertIn('auction', bid)
        self.assertIsInstance(bid['auction'], int)
        self.assertIn('work_offers', bid)
        self.assertTrue(bid['work_offers'])

    def test_admin_create(self):
        self.create(case_admin, 'manager', True)

    def test_admin_collection(self):
        self.collection(case_admin, 'manager')

    def test_admin_view(self):
        self.view(case_admin, 'manager', True)

    def test_admin_modify(self):
        self.modify(case_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'manager', True)

    def test_contractor_create(self):
        self.create(case_contractor, 'contractor', True)

    def test_contractor_delete(self):
        self.delete(case_contractor, 'contractor', True)

    def test_contractor_collection(self):
        self.collection(case_contractor, 'contractor')

    def test_contractor_view(self):
        self.view(case_contractor, 'contractor', True)

    def test_contractor_modify(self):
        self.modify(case_contractor, 'contractor', True)

    def test_mgr_collection(self):
        self.collection(case_mgr, 'manager')

    def test_mgr_view(self):
        self.view(case_mgr, 'manager', True)

    def test_mgr_modify(self):
        self.modify(case_mgr, 'manager', False)

    def test_mgr_delete(self):
        self.delete(case_mgr, 'manager', False)

    def test_mgr_create(self):
        self.create(case_mgr, 'manager', False)
