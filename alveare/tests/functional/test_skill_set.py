from copy import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from alveare.common.mock import create_one_user
from alveare.common.utils import AlveareResource, validate_resource_collection
from alveare.tests.common.skill_set import (
    case_mgr,
    case_contractor,
)


class TestSkillSetResource(AlveareRestTestCase):
    def setUp(self):
        self.skill_set_resource = AlveareResource(self, 'SkillSet')
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
        contractor = AlveareResource(self, 'Contractor').get_any()
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
        AlveareResource(self, 'Contractor').delete(**skill_set['contractor'])
        self.get_resource(self.skill_set_resource.url(skill_set), 404)

class TestSkillSet(AlveareNoMockRestTestCase):
    def setUp(self):
        self.resource = AlveareResource(self, 'SkillSet')
        super().setUp()

    def _test_skill_set(self, case, create, modify, delete, view):
        user, skill_set = case(self.db)
        validate_resource_collection(self, user, [skill_set])
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
        self.login_admin()
        skill_set_blob = self.resource.get(skill_set.id)
        self.resource.update(**skill_set_blob)
        self.resource.delete(**skill_set_blob)
        new_skill_set_blob = copy(skill_set_blob)
        del new_skill_set_blob['id']
        self.resource.create(**new_skill_set_blob)

    def test_mgr(self):
        self._test_skill_set(case_mgr, False, False, False, True)

    def test_contractor(self):
        self._test_skill_set(case_contractor, True, True, True, True)
