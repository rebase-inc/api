from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestCodeClearanceResource(AlveareRestTestCase):
    def setUp(self):
        self.code_clearance_resource = AlveareResource(self, 'CodeClearance')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        code_clearance = self.code_clearance_resource.get_any()
        self.assertTrue(code_clearance) # mock should have created at least one account
        self.assertTrue(code_clearance['id'])
        self.assertTrue(code_clearance['contractor'])
        self.assertTrue(code_clearance['project'])

    def test_get_one_unauthorized(self):
        self.login_admin()
        code_clearance = self.code_clearance_resource.get_any()
        self.login_as_new_user()
        self.code_clearance_resource.get(code_clearance, 401)
        self.login_admin()
        self.code_clearance_resource.get(code_clearance)

    def test_create(self):
        self.login_admin()
        contractor =    AlveareResource(self, 'Contractor').get_any()
        project =       AlveareResource(self, 'Project').get_any()
        code_clearance = dict(
            pre_approved=   True,
            project = dict(id=project['id']),
            contractor=  dict(id=contractor['id'])
        )
        self.code_clearance_resource.create(**code_clearance)

    def test_update(self):
        self.login_admin()
        code_clearance = self.code_clearance_resource.get_any()
        code_clearance['pre_approved'] = not code_clearance['pre_approved']
        self.code_clearance_resource.update(**code_clearance)

    def test_update_unauthorized(self):
        self.login('steve@alveare.io', 'foo')
        code_clearance = self.code_clearance_resource.get_any()
        code_clearance['pre_approved'] = not code_clearance['pre_approved']
        self.code_clearance_resource.update(401, **code_clearance)

    def test_delete(self):
        self.login_admin()
        self.code_clearance_resource.delete_any()

    def test_delete_project(self):
        self.login_admin()
        code_clearance = self.code_clearance_resource.get_any()
        self.delete_resource('projects/{}'.format(code_clearance['project']['id']))
        self.get_resource(self.code_clearance_resource.url(code_clearance), 404)

    def test_delete_contractor(self):
        self.login_admin()
        code_clearance = self.code_clearance_resource.get_any()
        self.delete_resource('contractors/{}'.format(code_clearance['contractor']['id']))
        self.get_resource(self.code_clearance_resource.url(code_clearance), 404)
