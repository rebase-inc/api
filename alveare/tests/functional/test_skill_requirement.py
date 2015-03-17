from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


# Note: there are no skill_requirement creation tests here because only
# children classes of skill_requirement have a valid constructor

class TestSkillRequirementResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'SkillRequirement')
        super().setUp()

    def test_get_one(self):
        skill_requirement = self.r.get_any()
        self.assertTrue(skill_requirement) # mock should have created at least one ticket and its related SkillRequirement object
        self.assertTrue(skill_requirement['id'])
        ticket = self.get('ticket', skill_requirement['id'])
        self.assertTrue(ticket)
        project = self.get('project', ticket['project_id'])
        self.assertEqual(ticket['skill_requirement']['id'], skill_requirement['id'])

    @skip('nothing to update in the SkillRequirement object yet')
    def test_update(self):
        skill_requirement = self.r.get_any()
        skill_requirement['some_field'] = 'better value'
        self.r.update(**skill_requirement) 

    def test_delete(self):
        self.r.delete_any()

    def test_delete_project(self):
        skill_requirement = self.r.get_any()
        ticket = self.get('ticket', skill_requirement['id'])
        self.delete_resource('projects/{}'.format(ticket['project_id']))
        self.get_resource(self.r.url(skill_requirement), 404)
