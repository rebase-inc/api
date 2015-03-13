from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestSkillSetResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'skill_set')
        super().setUp()

    def test_get_one(self):
        skill_set = self.r.get_any()
        self.assertTrue(skill_set) # mock should have created at least one account
        self.assertTrue(skill_set['id'])
        self.assertTrue(skill_set['contractor'])
        self.assertEqual(skill_set['contractor']['id'], skill_set['id'])

    def test_create(self):
        contractor = AlveareResource(self, 'contractor').get_any()
        skill_set = dict(
            contractor={ 'id': contractor['id'] }
        )
        new_skill_set = self.r.create(**skill_set)

    def test_update(self):
        skill_set = self.r.get_any()
        # nothing to update yet!
        self.r.update(**skill_set) 

    def test_delete(self):
        self.r.delete_any()

    def test_delete_project(self):
        skill_set = self.r.get_any()
        c = AlveareResource(self, 'contractor').delete(skill_set['contractor'])
        self.get_resource(self.r.url(skill_set), 404)
