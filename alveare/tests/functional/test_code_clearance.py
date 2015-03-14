from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestCodeClearanceResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'code_clearance')
        super().setUp()

    def test_get_one(self):
        code_clearance = self.r.get_any()
        self.assertTrue(code_clearance) # mock should have created at least one account
        self.assertTrue(code_clearance['id'])
        self.assertTrue(code_clearance['contractor'])
        self.assertTrue(code_clearance['project'])

    def test_create(self):
        contractor =    AlveareResource(self, 'contractor').get_any()
        project =       AlveareResource(self, 'project').get_any()
        code_clearance = dict(
            pre_approved=   True,
            project = dict(id=project['id']),
            contractor=  dict(id=contractor['id'])
        )
        self.r.create(**code_clearance)

    def test_update(self):
        code_clearance = self.r.get_any()
        code_clearance['pre_approved'] = not code_clearance['pre_approved']
        self.r.update(**code_clearance)

    def test_delete(self):
        self.r.delete_any()

    def test_delete_project(self):
        code_clearance = self.r.get_any()
        self.delete_resource('projects/{}'.format(code_clearance['project']['id']))
        self.get_resource(self.r.url(code_clearance), 404)

    def test_delete_contractor(self):
        code_clearance = self.r.get_any()
        self.delete_resource('contractors/{}'.format(code_clearance['contractor']['id']))
        self.get_resource(self.r.url(code_clearance), 404)
