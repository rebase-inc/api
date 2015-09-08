from copy import copy

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.common.mock import create_one_user, create_admin_user
from rebase.common.utils import RebaseResource, validate_resource_collection
from rebase.tests.common.skill_set import (
    case_mgr,
    case_contractor,
)


class TestSkillSetResource(RebaseRestTestCase):
    def setUp(self):
        self.skill_set_resource = RebaseResource(self, 'SkillSet')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        skill_set = self.skill_set_resource.get_any()
        self.assertTrue(skill_set) # mock should have created at least one account
        self.assertTrue(skill_set['id'])
        self.assertTrue(skill_set['contractor'])
        self.assertEqual(skill_set['contractor']['id'], skill_set['id'])

    def test_create(self):
        self.login_admin()
        contractor = RebaseResource(self, 'Contractor').get_any()
        skill_set = dict(
            contractor={ 'id': contractor['id'] }
        )
        new_skill_set = self.skill_set_resource.create(**skill_set)

    def test_update(self):
        self.login_admin()
        skill_set = self.skill_set_resource.get_any()
        # nothing to update yet!
        self.skill_set_resource.update(**skill_set) 

    def test_delete(self):
        self.login_admin()
        self.skill_set_resource.delete_any()

    def test_delete_contractor(self):
        self.login_admin()
        skill_set = self.skill_set_resource.get_any()
        RebaseResource(self, 'Contractor').delete(**skill_set['contractor'])
        self.get_resource(self.skill_set_resource.url(skill_set), 404)

class TestSkillSet(RebaseNoMockRestTestCase):
    def setUp(self):
        self.resource = RebaseResource(self, 'SkillSet')
        super().setUp()

    def _test_skill_set(self, case, role, create, modify, delete, view):
        user, skill_set = self._run(case, role)
        validate_resource_collection(self, [skill_set])
        skill_set_blob = self.resource.get(skill_set.id, 200 if view else 401)
        self.resource.update(expected_status=200 if modify else 401, **skill_set_blob)
        self.resource.delete(expected_status=200 if delete else 401, **skill_set_blob)
        new_skill_set_blob = copy(skill_set_blob)
        del new_skill_set_blob['id']
        self.resource.create(expected_status=201 if create else 401, **new_skill_set_blob)
        
        # negative tests
        user, skill_set = case(self.db)
        other_user = create_one_user(self.db)
        self.login(other_user.email, 'foo')
        self.resource.get(skill_set.id, 401)
        self.resource.update(expected_status=401, **skill_set_blob)
        self.resource.delete(expected_status=401, **skill_set_blob)
        self.resource.create(expected_status=401, **new_skill_set_blob)

        # admin tests
        admin_user = create_admin_user(self.db, password='foo')
        self.login(admin_user.email, 'foo')
        skill_set_blob = self.resource.get(skill_set.id)
        self.resource.update(**skill_set_blob)
        self.resource.delete(**skill_set_blob)
        new_skill_set_blob = copy(skill_set_blob)
        del new_skill_set_blob['id']
        self.resource.create(**new_skill_set_blob)

    def test_mgr(self):
        self._test_skill_set(case_mgr, 'manager', False, False, False, True)

    def test_contractor(self):
        self._test_skill_set(case_contractor, 'contractor', False, False, False, True)
