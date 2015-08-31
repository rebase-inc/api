from unittest import skip
from copy import copy

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.common.mock import create_one_user, create_admin_user
from rebase.common.utils import RebaseResource, validate_resource_collection
from rebase.tests.common.skill_requirement import (
    case_mgr,
    case_contractor,
)


# Note: there are no skill_requirement creation tests here because only
# children classes of skill_requirement have a valid constructor

class TestSkillRequirementResource(RebaseRestTestCase):
    def setUp(self):
        self.skill_requirement_resource = RebaseResource(self, 'SkillRequirement')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        skill_requirement = self.skill_requirement_resource.get_any()
        self.assertTrue(skill_requirement) # mock should have created at least one ticket and its related SkillRequirement object
        self.assertTrue(skill_requirement['id'])
        ticket = self.get_resource('tickets/{id}'.format(**skill_requirement))['ticket']
        self.assertTrue(ticket)
        project = self.get_resource('projects/{id}'.format(**ticket['project']))
        self.assertEqual(ticket['skill_requirement']['id'], skill_requirement['id'])

    @skip('nothing to update in the SkillRequirement object yet')
    def test_update(self):
        self.login_admin()
        skill_requirement = self.skill_requirement_resource.get_any()
        skill_requirement['some_field'] = 'better value'
        self.skill_requirement_resource.update(**skill_requirement) 

    def test_delete(self):
        self.login_admin()
        self.skill_requirement_resource.delete_any()

    def test_delete_project(self):
        self.login_admin()
        skill_requirement = self.skill_requirement_resource.get_any()
        ticket = self.get_resource('tickets/{id}'.format(**skill_requirement))['ticket']
        self.delete_resource('projects/{id}'.format(**ticket['project']))
        self.get_resource(self.skill_requirement_resource.url(skill_requirement), 404)

class TestSkillRequirement(RebaseNoMockRestTestCase):
    def setUp(self):
        self.resource = RebaseResource(self, 'SkillRequirement')
        super().setUp()

    def _test_skill_requirement(self, case, create, modify, delete, view):
        user, skill_requirement = case(self.db)
        validate_resource_collection(self, user, [skill_requirement] if skill_requirement else [])
        if skill_requirement:
            skill_requirement_blob = self.resource.get(skill_requirement.id, 200 if view else 401)
            self.resource.update(expected_status=200 if modify else 401, **skill_requirement_blob)
            self.resource.delete(expected_status=200 if delete else 401, **skill_requirement_blob)
            new_skill_requirement_blob = copy(skill_requirement_blob)
            del new_skill_requirement_blob['id']
            new_skill_requirement_blob['foo'] = 'bar'
            self.resource.create(expected_status=201 if create else 401, **new_skill_requirement_blob)
        
        # negative tests
        user, skill_requirement = case(self.db)
        other_user = create_one_user(self.db)
        self.login(other_user.email, 'foo')
        if skill_requirement:
            self.resource.get(skill_requirement.id, 401)
            self.resource.update(expected_status=401, **skill_requirement_blob)
            self.resource.delete(expected_status=401, **skill_requirement_blob)
            self.resource.create(expected_status=401, **new_skill_requirement_blob)

        # admin tests
        admin_user = create_admin_user(self.db, password='foo')
        self.login(admin_user.email, 'foo')
        if skill_requirement:
            skill_requirement_blob = self.resource.get(skill_requirement.id)
            self.resource.update(**skill_requirement_blob)
            self.resource.delete(**skill_requirement_blob)
            new_skill_requirement_blob = copy(skill_requirement_blob)
            del new_skill_requirement_blob['id']
            self.resource.create(**new_skill_requirement_blob)

    def test_mgr(self):
        self._test_skill_requirement(case_mgr, False, False, False, True)

    def test_contractor(self):
        self._test_skill_requirement(case_contractor, False, False, False, False)
