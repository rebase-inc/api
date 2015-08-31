from functools import partial

from . import PermissionTestCase

from rebase.models import Bid, Contractor, Manager
from rebase.common.utils import ids
from rebase.tests.common.bid import case_mgr, case_contractor, case_admin


def _new_instance(instance):
    return {
        'auction': ids(instance.auction),
        'contractor': ids(instance.contractor),
        'work_offers': [ ids(wo) for wo in instance.work_offers.all() ]
    }

class TestBid(PermissionTestCase):
    model = 'Bid'

    _create = partial(PermissionTestCase._create, new_instance=_new_instance)

    def test_admin_create(self):
        TestBid._create(self, case_admin, True)

    def test_admin_collection(self):
        self._collection(case_admin)

    def test_admin_view(self):
        self._view(case_admin, True)

    def test_admin_modify(self):
        self._modify(case_admin, True)

    def test_admin_delete(self):
        self._delete(case_admin, True)

    def test_contractor_create(self):
        TestBid._create(self, case_contractor, True)

    def test_contractor_delete(self):
        self._delete(case_contractor, True)

    def test_contractor_collection(self):
        self._collection(case_contractor)

    def test_contractor_view(self):
        self._view(case_contractor, True)

    def test_contractor_modify(self):
        self._modify(case_contractor, True)

    def test_mgr_collection(self):
        self._collection(case_mgr)

    def test_mgr_view(self):
        self._view(case_mgr, True)

    def test_mgr_modify(self):
        self._modify(case_mgr, False)

    def test_mgr_delete(self):
        self._delete(case_mgr, False)

    def test_mgr_create(self):
        TestBid._create(self, case_mgr, False)

