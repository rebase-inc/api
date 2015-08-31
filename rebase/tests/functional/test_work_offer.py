from functools import partial
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

def _new_instance(work_offer):
    return {
        'contractor':       ids(work_offer.contractor),
        'ticket_snapshot':  ids(work_offer.ticket_snapshot),
        'price':            floor(.9*work_offer.price)
    }

def _modify_this(work_offer):
    new = _new_instance(work_offer)
    new.update(ids(work_offer))
    new['price'] = floor(new['price']*.7)
    return new

def _validate_work_offer(test, work_offer):
    test.assertIsInstance(work_offer.pop('id'), int)
    test.assertIsInstance(work_offer.pop('work', 1), int)
    test.assertIsInstance(work_offer.pop('price'), int)
    snapshot = work_offer.pop('ticket_snapshot')
    test.assertIn('id', snapshot)
    test.assertIsInstance(work_offer.pop('contractor'), dict)
    test.assertEqual(work_offer, {})

class TestWorkOffer(PermissionTestCase):
    model = 'WorkOffer'
    _create = partial(PermissionTestCase._create, new_instance=_new_instance)
    _view = partial(PermissionTestCase._view, validate=_validate_work_offer)
    _modify = partial(PermissionTestCase._modify, modify_this=_modify_this)

    def test_mgr_delete(self):
        self._delete(case_mgr, False)

    def test_mgr_collection(self):
        self._collection(case_mgr_collection)

    def test_mgr_modify(self):
        TestWorkOffer._modify(self, case_mgr, False)

    def test_mgr_view(self):
        TestWorkOffer._view(self, case_mgr, True)

    def test_mgr_create(self):
        mgr_user, work_offer, snapshot_2 = case_mgr_create(self.db)

        work_offer_2 = {
            'contractor':       ids(work_offer.contractor),
            'ticket_snapshot':  ids(snapshot_2),
            'price':            floor(.9*work_offer.price)
        }

        super()._create(lambda db: (mgr_user, work_offer), False, new_instance=lambda _: work_offer_2)

    def test_contractor_delete(self):
        self._delete(case_contractor, True)

    def test_contractor_collection(self):
        self._collection(case_contractor)

    def test_contractor_modify(self):
        TestWorkOffer._modify(self, case_contractor, True)

    def test_contractor_view(self):
        TestWorkOffer._view(self, case_contractor, True)

    def test_contractor_create(self):
        TestWorkOffer._create(self, case_contractor, True, delete_first=True)
