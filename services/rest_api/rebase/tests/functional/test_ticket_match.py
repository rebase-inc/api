from copy import copy

from . import RebaseRestTestCase, RebaseNoMockRestTestCase
from rebase.common.mock import create_one_user
from rebase.common.utils import RebaseResource, validate_resource_collection, ids
from rebase.tests.common.ticket_match import (
    case_mgr,
    case_contractor,
    case_admin
)


class TestTicketMatchResource(RebaseRestTestCase):
    def setUp(self):
        self.ticket_match_resource =        RebaseResource(self, 'TicketMatch')
        self.skill_set_resource =           RebaseResource(self, 'SkillSet')
        self.skill_requirement_resource =   RebaseResource(self, 'SkillRequirement')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        ticket_match = self.ticket_match_resource.get_any()
        self.assertTrue(ticket_match) # mock should have created at least one ticket and its related TicketMatch object
        self.assertTrue(self.skill_requirement_resource.get(ticket_match['skill_requirement']))
        self.assertTrue(self.skill_set_resource.get(ticket_match['skill_set']))

    def test_create(self):
        self.login_admin()
        self.ticket_match_resource.create(
            skill_requirement = {'id': self.skill_requirement_resource.get_any()['id']},
            skill_set =         {'id': self.skill_set_resource.get_any()['id']},
            score = 789
        )

    def test_update(self):
        self.login_admin()
        ticket_match = self.ticket_match_resource.get_any()
        ticket_match['score'] = 123
        self.ticket_match_resource.update(**ticket_match)

    def test_delete(self):
        self.login_admin()
        self.ticket_match_resource.delete_any()

    def test_delete_skill_requirement(self):
        self.login_admin()
        ticket_match = self.ticket_match_resource.get_any()
        self.skill_requirement_resource.delete(**ticket_match['skill_requirement'])
        self.ticket_match_resource.get(ticket_match, 404)

    def test_delete_skill_set(self):
        self.login_admin()
        ticket_match = self.ticket_match_resource.get_any()
        self.skill_set_resource.delete(**ticket_match['skill_set'])
        self.ticket_match_resource.get(ticket_match, 404)

class TestTicketMatch(RebaseNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = RebaseResource(self, 'TicketMatch')
        
    def _test_ticket_match(self, case, role, create=True, modify=True, delete=True, view=True):
        user, ticket_match = self._run(case, role)
        if ticket_match:
            validate_resource_collection(self, [ticket_match])
        if view:
            ticket_match_blob = self.resource.get(ids(ticket_match)) 
        if modify:
            self.resource.update(**ticket_match_blob)
        if delete:
            self.resource.delete(**ticket_match_blob)
        if create and view:
            new_ticket_match_blob = copy(ticket_match_blob)
            del new_ticket_match_blob['skill_requirement_id']
            del new_ticket_match_blob['skill_set_id']
            self.resource.create(**new_ticket_match_blob)
        
        # negative tests
        user, ticket_match = case(self.db)
        other_user = create_one_user(self.db)
        self.login(other_user.email, 'foo')
        if view:
            self.resource.get(
                {
                    'skill_requirement_id': ticket_match.skill_requirement_id,
                    'skill_set_id': ticket_match.skill_set_id
                },
                401
            )
            self.resource.update(expected_status=401, **ticket_match_blob)
            self.resource.delete(expected_status=401, **ticket_match_blob)
        if create and view:
            self.resource.create(expected_status=401, **new_ticket_match_blob)

    def test_mgr(self):
        self._test_ticket_match(case_mgr, 'manager', False, False, False, True)

    def test_contractor(self):
        self._test_ticket_match(case_contractor, 'contractor', False, False, False, False)

    def test_admin(self):
        self._test_ticket_match(case_admin, 'manager')
