from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestTicketMatchResource(AlveareRestTestCase):
    def setUp(self):
        self.r =    AlveareResource(self, 'TicketMatch')
        self.ss =   AlveareResource(self, 'SkillSet')
        self.sr =   AlveareResource(self, 'SkillRequirement')
        super().setUp()

    def test_get_one(self):
        ticket_match = self.r.get_any()
        self.assertTrue(ticket_match) # mock should have created at least one ticket and its related TicketMatch object
        self.assertTrue(self.sr.get(ticket_match['skill_requirement']))
        self.assertTrue(self.ss.get(ticket_match['skill_set']))

    def test_create(self):
        self.r.create(
            skill_requirement = {'id': self.sr.get_any()['id']},
            skill_set =         {'id': self.ss.get_any()['id']},
            score = 789
        )

    def test_update(self):
        ticket_match = self.r.get_any()
        ticket_match['score'] = 123
        self.r.update(**ticket_match) 

    def test_delete(self):
        self.r.delete_any()

    def test_delete_skill_requirement(self):
        ticket_match = self.r.get_any()
        skill_requirement = self.sr.get(ticket_match['skill_requirement'])
        self.sr.delete(skill_requirement)
        self.sr.get(skill_requirement, 404)

    def test_delete_skill_set(self):
        ticket_match = self.r.get_any()
        skill_set = self.sr.get(ticket_match['skill_set'])
        self.sr.delete(skill_set)
        self.sr.get(skill_set, 404)
