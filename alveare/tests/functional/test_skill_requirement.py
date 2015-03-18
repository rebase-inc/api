from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


# Note: there are no skill_requirement creation tests here because only
# children classes of skill_requirement have a valid constructor

class TestSkillRequirementResource(AlveareRestTestCase):
    def setUp(self):
        self.skill_requirement_resource = AlveareResource(self, 'SkillRequirement')
        super().setUp()

    def test_get_one(self):
        skill_requirement = self.skill_requirement_resource.get_any()
        self.assertTrue(skill_requirement) # mock should have created at least one ticket and its related SkillRequirement object
        self.assertTrue(skill_requirement['id'])
        ticket = self.get_resource('tickets/{id}'.format(**skill_requirement))['ticket']
        self.assertTrue(ticket)
        project = self.get_resource('projects/{id}'.format(**ticket['project']))
        self.assertEqual(ticket['skill_requirement']['id'], skill_requirement['id'])

    @skip('nothing to update in the SkillRequirement object yet')
    def test_update(self):
        skill_requirement = self.skill_requirement_resource.get_any()
        skill_requirement['some_field'] = 'better value'
        self.skill_requirement_resource.update(**skill_requirement) 

    def test_delete(self):
        self.skill_requirement_resource.delete_any()

    def test_delete_project(self):
        skill_requirement = self.skill_requirement_resource.get_any()
        ticket = self.get_resource('tickets/{id}'.format(**skill_requirement))['ticket']
        self.delete_resource('projects/{id}'.format(**ticket['project']))
        self.get_resource(self.skill_requirement_resource.url(skill_requirement), 404)
