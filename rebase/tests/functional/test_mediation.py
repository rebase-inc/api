from datetime import timedelta

from . import RebaseRestTestCase

from . import PermissionTestCase
from rebase.common.utils import ids
from rebase.models import Mediation
from rebase.tests.common.mediation import MediationUseCase

class TestMediation(PermissionTestCase):
    model = 'Mediation'

    def setUp(self):
        super().setUp()
        self.case = MediationUseCase()

    def new(_, old_instance):
        return {
            'work': ids(old_instance.work),
            'timeout': old_instance.timeout.isoformat()
        }

    def update(_, mediation):
        updated_mediation = ids(mediation)
        updated_mediation.update(timeout=(mediation.timeout + timedelta(days=3)).isoformat())
        return updated_mediation

    def validate_modify(_, test_resource, requested, returned):
        # TODO re-implement with datetime comparison
        pass

    def validate_view(self, mediation):
        self.assertIsInstance(mediation.pop('id'), int)
        self.assertIsInstance(mediation.pop('timeout'), str)
        self.assertIsInstance(mediation.pop('state'), str)
        #self.assertIsInstance(mediation.pop('work'), int)
        #self.assertIsInstance(mediation.pop('comments'), dict)
        
    def test_user_1_as_mgr_collection(self):
        self.collection(self.case.user_1_as_mgr, 'manager')

    def test_user_1_as_mgr_view(self):
        self.view(self.case.user_1_as_mgr, 'manager', True)

    def test_user_1_as_mgr_modify(self):
        self.modify(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_delete(self):
        self.delete(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_mgr_create(self):
        self.create(self.case.user_1_as_mgr, 'manager', False)

    def test_user_1_as_contractor_collection(self):
        self.collection(self.case.user_1_as_contractor, 'contractor')

    def test_user_1_as_contractor_view(self):
        self.view(self.case.user_1_as_contractor, 'contractor', True)

    def test_user_1_as_contractor_modify(self):
        self.modify(self.case.user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_delete(self):
        self.delete(self.case.user_1_as_contractor, 'contractor', False)

    def test_user_1_as_contractor_create(self):
        self.create(self.case.user_1_as_contractor, 'contractor', False, delete_first=True)

    def test_user_2_as_mgr_collection(self):
        self.collection(self.case.user_2_as_mgr, 'manager')

    def test_user_2_as_mgr_view(self):
        self.view(self.case.user_2_as_mgr, 'manager', True)

    def test_user_2_as_mgr_modify(self):
        self.modify(self.case.user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_delete(self):
        self.delete(self.case.user_2_as_mgr, 'manager', False)

    def test_user_2_as_mgr_create(self):
        self.create(self.case.user_2_as_mgr, 'manager', False, delete_first=True)

    def test_user_2_as_contractor_collection(self):
        self.collection(self.case.user_2_as_contractor, 'contractor')

    def test_user_2_as_contractor_view(self):
        self.view(self.case.user_2_as_contractor, 'contractor', True)

    def test_user_2_as_contractor_modify(self):
        self.modify(self.case.user_2_as_contractor, 'contractor', False)

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
