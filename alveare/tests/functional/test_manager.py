import json
import time

from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource

def mgr_url(id):
    return '/managers/{}'.format(id)

class TestManagerResource(AlveareRestTestCase):
    def setUp(self):
        self.manager_resource = AlveareResource(self, 'Manager')
        self.org_resource = AlveareResource(self, 'Organization')
        self.project_resource = AlveareResource(self, 'Project')
        self.clearance_resource = AlveareResource(self, 'CodeClearance')
        self.contractor_resource = AlveareResource(self, 'Contractor')
        self.user_resource = AlveareResource(self, 'User')
        super().setUp()

    def test_get_all_as_admin(self):
        self.login_admin()
        self.assertTrue(self.manager_resource.get_all())

    def _test_one_manager_object_for_manager(self, manager, user):
        ''' validate the 'manager' object from the perspective of user-manager '''
        self.assertIn('user', manager)
        self.assertIn('id', manager['user'])
        self.assertEqual(manager['user']['id'], user.id)

    def test_get_all_as_manager(self):
        user = self.login_as_manager_only()
        managers = self.manager_resource.get_all()
        self.assertTrue(managers)
        for manager in managers:
            self._test_one_manager_object_for_manager(manager, user)

    def _test_one_manager_object_for_contractor(self, manager, user):
        self.assertIn('organization', manager)
        self.assertIn('id', manager['organization'])
        org = self.org_resource.get(manager['organization'])
        self.assertTrue(org)
        self.assertIn('projects', org)
        projects = org['projects']
        self.assertTrue(projects)
        for prj in projects:
            project = self.project_resource.get(prj)
            self.assertTrue(project)
            self.assertIn('clearances', project)
            clearances = project['clearances']
            found_user = False
            for clr in clearances:
                clearance = self.clearance_resource.get(clr)
                contractor = self.contractor_resource.get(clearance['contractor'])
                found_user = contractor['user']['id'] == user.id
                if found_user:
                    break
            self.assertTrue(found_user)

    def test_get_all_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        managers = self.manager_resource.get_all()
        self.assertTrue(managers)
        for manager in managers:
            self._test_one_manager_object_for_contractor(manager, user)

    def test_get_one_as_admin(self):
        user = self.login_admin()
        self.assertTrue(self.project_resource.get_any())

    def test_get_one_as_manager(self):
        user = self.login_as_manager_only()
        self._test_one_manager_object_for_manager(
            self.manager_resource.get_any(),
            user
        )

    def test_get_one_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        self._test_one_manager_object_for_contractor(
            self.manager_resource.get_any(),
            user
        )

    def create_new_manager(self, organization, expected_status=201):
        # create a new user and make him a manager for this organization

        def validate_user(self, resource, response):
            del resource['password']
            return self.validate_response(resource, response)

        user = self.user_resource.create(
            validate=validate_user,
            expected_status=201,
            first_name='Saul',
            last_name='Goodman',
            email='saulgoodman@alveare.io',
            password='foo'
        )
        user = self.user_resource.just_ids(user)

        organization = self.org_resource.just_ids(organization)
        new_manager = self.manager_resource.create(
            validate=None,
            expected_status=expected_status,
            user=user,
            organization=organization
        )
        return new_manager

    def test_create_as_admin(self):
        self.login_admin()
        org = self.org_resource.get_any()
        new_mgr = self.create_new_manager(org)
        self.assertTrue(new_mgr)

    def test_create_as_manager(self):
        user = self.login_as_manager_only()
        org = user.roles.first().organization
        new_mgr = self.create_new_manager({'id': org.id})
        self.assertTrue(new_mgr)

    def test_create_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        org = user.roles.first().clearances[0].project.organization
        new_mgr = self.create_new_manager({'id':org.id}, 401)
        self.assertFalse(new_mgr)

    def _test_delete(self, org, expected_status=200):
        new_mgr = self.create_new_manager(org)
        self.manager_resource.delete(expected_status=expected_status, **new_mgr)
        self.manager_resource.get(new_mgr, 404)

    def test_delete_as_admin(self):
        self.login_admin()
        org = self.org_resource.get_any()
        self.assertTrue(org)
        self._test_delete(org)

    def test_delete_as_manager(self):
        user = self.login_as_manager_only()
        org = user.roles.first().organization
        self._test_delete({'id':org.id})

    def test_delete_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        org = user.roles.first().clearances[0].project.organization
        self.assertTrue(org.managers)
        mgr = org.managers[0]
        self.manager_resource.delete(expected_status=401, id=mgr.id)
        
    def _test_update(self, expected_status=200):
        mgr = self.manager_resource.get_any()
        self.assertTrue(mgr)
        self.manager_resource.update(expected_status=expected_status, **mgr)
        
    def test_update_as_admin(self):
        self.login_admin()
        self._test_update()

    def test_update_as_manager(self):
        self.login_as_manager_only()
        self._test_update()

    def test_update_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        self._test_update(401)
