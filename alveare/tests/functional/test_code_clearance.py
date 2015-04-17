from . import AlveareRestTestCase
from sqlalchemy import and_
from alveare.common.utils import AlveareResource
from alveare.models import (
    Contractor,
    Project,
    User,
    Manager,
    CodeClearance,
    Organization,
    Role,
)
from unittest import skip

class TestCodeClearanceResource(AlveareRestTestCase):
    def setUp(self):
        self.code_clearance_resource = AlveareResource(self, 'CodeClearance')
        self.contractor_resource = AlveareResource(self, 'Contractor')
        super().setUp()

    def test_get_all_as_admin(self):
        self.logout()
        self.assertFalse(self.code_clearance_resource.get_all(401))
        self.login_admin()
        clearances = self.code_clearance_resource.get_all()
        self.assertTrue(clearances)

    def test_get_all_as_contractor(self):
        user = self.login_as_contractor_only()
        clearances = self.code_clearance_resource.get_all()
        self.assertTrue(clearances)
        for clearance in clearances:
            contractor = self.contractor_resource.get(clearance['contractor'])
            with self.subTest(clearance_id=clearance['id']):
                self.assertEqual(contractor['user']['id'], user.id)

    def test_get_all_as_manager(self):
        manhattan_project = Project.query.filter(Project.name=='Manhattan').first()
        user = manhattan_project.organization.managers[0].user
        self.login(user.email, 'foo')
        clearances = self.code_clearance_resource.get_all()
        self.assertTrue(clearances)
        for clearance in clearances:
            contractor = self.contractor_resource.get(clearance['contractor'])
            self.assertNotEqual(contractor['user']['id'], user.id)

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
            project =       dict(id=project['id']),
            contractor=     dict(id=contractor['id'])
        )
        self.code_clearance_resource.create(**code_clearance)

    def test_create_unauthorized(self):
        project = Project.query.first()
        contractor = Contractor.query\
            .join(User)\
            .join(Manager)\
            .filter(Manager.organization != project.organization).first()

        self.login(contractor.user.email, 'foo')
        code_clearance = dict(
            pre_approved=   True,
            project =       dict(id=project.id),
            contractor=     dict(id=contractor.id)
        )
        self.code_clearance_resource.create(expected_status=401, **code_clearance)

    def test_update(self):
        self.login_admin()
        code_clearance = self.code_clearance_resource.get_any()
        code_clearance['pre_approved'] = not code_clearance['pre_approved']
        self.code_clearance_resource.update(**code_clearance)

    def test_update_unauthorized(self):
        self.login('steve@alveare.io', 'foo')
        code_clearance = self.code_clearance_resource.get_any()
        code_clearance['pre_approved'] = not code_clearance['pre_approved']
        self.code_clearance_resource.update(expected_status=401, **code_clearance)

    def test_delete(self):
        self.login_admin()
        self.code_clearance_resource.delete_any()

    def test_delete_unauthorized(self):
        code_clearance = CodeClearance.query.first()
        unauthorized_user = User.query\
            .join(Manager)\
            .filter(Manager.organization != code_clearance.project.organization)\
            .filter(~User.admin)\
            .first()

        self.code_clearance_resource.delete(expected_status=401, id=code_clearance.id)

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
