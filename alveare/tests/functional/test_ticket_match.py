from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestTicketMatchResource(AlveareRestTestCase):
    def setUp(self):
        self.ticket_match_resource =        AlveareResource(self, 'TicketMatch')
        self.skill_set_resource =           AlveareResource(self, 'SkillSet')
        self.skill_requirement_resource =   AlveareResource(self, 'SkillRequirement')
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
