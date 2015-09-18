from . import PermissionTestCase
from rebase.common.utils import ids
from rebase.tests.common.review import ReviewUseCase


class TestReview(PermissionTestCase):
    model = 'Review'

    def setUp(self):
        super().setUp()
        self.case = ReviewUseCase()

    def validate_view(self, review):
        self.assertIsInstance(review.pop('id'), int)
        self.assertIsInstance(review.pop('rating'), int)
        self.assertIsInstance(review.pop('comments'), list)
        self.assertIsInstance(review.pop('work'), dict)

    def update(_, review):
        updated_review = ids(review)
        updated_review.update(rating=(review.rating+1)%5)
        return updated_review

    def new(_, instance):
        return {
            'work': ids(instance.work),
            'rating': instance.rating
        }
        
    def test_user_1_as_mgr_collection(self):
        self.collection(self.case.user_1_as_mgr, 'manager')

    def test_user_1_as_mgr_view(self):
        self.view(self.case.user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_modify(self):
        self.modify(self.case.user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_delete(self):
        self.delete(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_create(self):
        self.create(self.case.user_1_as_mgr, 'manager', False, delete_first=True)

    def test_user_1_as_contractor_collection(self):
        self.collection(self.case.user_1_as_contractor, 'contractor')

    def test_user_1_as_contractor_view(self):
        self.view(self.case.user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_modify(self):
        self.modify(self.case.user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_delete(self):
        self.delete(self.case.user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_create(self):
        self.create(self.case.user_1_as_contractor, 'contractor', False, delete_first=True)

    def test_user_2_as_mgr_collection(self):
        self.collection(self.case.user_2_as_mgr, 'manager')

    def test_user_2_as_mgr_view(self):
        self.view(self.case.user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_modify(self):
        self.modify(self.case.user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_delete(self):
        self.delete(self.case.user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_create(self):
        self.create(self.case.user_2_as_mgr, 'manager', False, delete_first=True)

    def test_user_2_as_contractor_collection(self):
        self.collection(self.case.user_2_as_contractor, 'contractor')

    def test_user_2_as_contractor_view(self):
        self.view(self.case.user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_modify(self):
        self.modify(self.case.user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_delete(self):
        self.delete(self.case.user_2_as_contractor, 'contractor', False)

    def test_user_2_as_contractor_create(self):
        self.create(self.case.user_2_as_contractor, 'contractor', False, delete_first=True)

    def test_admin_collection(self):
        self.collection(self.case.admin_collection, 'manager')

    def test_admin_view(self):
        self.view(self.case.admin, 'contractor', True)

    def test_admin_modify(self):
        self.modify(self.case.admin, 'contractor', True)

    def test_admin_delete(self):
        self.delete(self.case.admin, 'contractor', True)

    def test_admin_create(self):
        self.create(self.case.admin, 'contractor', True, delete_first=True)

    def test_deserialization(self):
        _, review = self._run(self.case.user_1_as_mgr, 'manager')
        self.post_resource('reviews', expected_code=400)
        response = self.post_resource('reviews', {'foo':'bar'}, expected_code=400)
        print(response)
