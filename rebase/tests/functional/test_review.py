from functools import partialmethod

from . import PermissionTestCase
from rebase.common.utils import ids
from rebase.tests.common.review import (
    case_user_1_as_mgr,
    case_user_1_as_contractor,
    case_user_2_as_mgr,
    case_user_2_as_contractor,
    case_admin,
    case_admin_collection,
)

def _new_instance(instance):
    return {
        'work': ids(instance.work),
        'rating': instance.rating
    }

def _modify_this(review):
    updated_review = ids(review)
    updated_review.update(rating=(review.rating+1)%5)
    return updated_review

class TestReview(PermissionTestCase):
    model = 'Review'
    _create = partialmethod(PermissionTestCase.create, new_instance=_new_instance, delete_first=True)

    def _validate(self, review):
        self.assertIsInstance(review.pop('id'), int)
        self.assertIsInstance(review.pop('rating'), int)
        self.assertIsInstance(review.pop('comments'), list)
        self.assertIsInstance(review.pop('work'), dict)

    _view = partialmethod(PermissionTestCase.view, validate=_validate)

    _modify = partialmethod(PermissionTestCase.modify, modify_this=_modify_this)
        
    def test_user_1_as_mgr_collection(self):
        self.collection(case_user_1_as_mgr, 'manager')

    def test_user_1_as_mgr_view(self):
        self._view(case_user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_modify(self):
        self._modify(case_user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_delete(self):
        self.delete(case_user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_create(self):
        self._create(case_user_1_as_mgr, 'manager', False)

    def test_user_1_as_contractor_collection(self):
        self.collection(case_user_1_as_contractor, 'contractor')

    def test_user_1_as_contractor_view(self):
        self._view(case_user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_modify(self):
        self._modify(case_user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_delete(self):
        self.delete(case_user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_create(self):
        self._create(case_user_1_as_contractor, 'contractor', False)

    def test_user_2_as_mgr_collection(self):
        self.collection(case_user_2_as_mgr, 'manager')

    def test_user_2_as_mgr_view(self):
        self._view(case_user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_modify(self):
        self._modify(case_user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_delete(self):
        self.delete(case_user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_create(self):
        self._create(case_user_2_as_mgr, 'manager', False)

    def test_user_2_as_contractor_collection(self):
        self.collection(case_user_2_as_contractor, 'contractor')

    def test_user_2_as_contractor_view(self):
        self._view(case_user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_modify(self):
        self._modify(case_user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_delete(self):
        self.delete(case_user_2_as_contractor, 'contractor', False)

    def test_user_2_as_contractor_create(self):
        self._create(case_user_2_as_contractor, 'contractor', False)

    def test_admin_collection(self):
        self.collection(case_admin_collection, 'manager')

    def test_admin_view(self):
        self._view(case_admin, 'contractor', True)

    def test_admin_modify(self):
        self._modify(case_admin, 'contractor', True)

    def test_admin_delete(self):
        self.delete(case_admin, 'contractor', True)

    def test_admin_create(self):
        self._create(case_admin, 'contractor', True)
