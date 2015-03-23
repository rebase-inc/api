from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


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
        AlveareResource(self, 'Contractor').delete(skill_set['contractor'])
        self.get_resource(self.skill_set_resource.url(skill_set), 404)
