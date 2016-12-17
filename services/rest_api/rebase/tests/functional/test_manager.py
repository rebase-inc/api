import json
import time

from . import RebaseRestTestCase
from rebase.common.mock import create_one_manager, create_one_organization
from rebase.common.utils import RebaseResource
from rebase.models.organization import Organization
from rebase.models.manager import Manager

def mgr_url(id):
    return '/managers/{}'.format(id)

class TestManagerResource(RebaseRestTestCase):
    def setUp(self):
        self.manager_resource =     RebaseResource(self, 'Manager')
        self.org_resource =         RebaseResource(self, 'Organization')
        self.project_resource =     RebaseResource(self, 'Project')
        self.clearance_resource =   RebaseResource(self, 'CodeClearance')
        self.contractor_resource =  RebaseResource(self, 'Contractor')
        self.user_resource =        RebaseResource(self, 'User')
        super().setUp()

    def test_get_all_as_admin(self):
        self.login_admin()
        self.assertTrue(self.manager_resource.get_all())

    def _test_one_manager_object_for_manager(self, manager, user):
        ''' validate the 'manager' object from the perspective of user-manager '''
        self.assertIn('user', manager)
        self.assertIn('id', manager['user'])

    def test_get_all_as_manager(self):
        user = self.login_as_manager_only()
        # We need to add an extra manager to the organizations this user has.
        # We also need to make sure this user has at least 2 orgs it manages.
        # This will make it easier to verify the queries are properly designed.
        orgs = Organization.query.join(Manager).filter(Manager.user==user).all()
        self.assertTrue(orgs)
        new_mgr = create_one_manager(self.db, org=orgs[0])
        if len(orgs) < 2:
            xxxx_org = create_one_organization(self.db, 'XXXX', user)
            xxxx_mgr = create_one_manager(self.db, org=xxxx_org)
        # at this point, user is a manager of at least 2 orgs, each with 2 mgrs at least.
        orgs = Organization.query.join(Manager).filter(Manager.user==user).all()
        total_managers = set()
        for org in orgs:
            total_managers |= set(org.managers)
        managers = self.manager_resource.get_all()
        self.assertEqual(len(total_managers), len(managers))
        total_managers_ids = {mgr.id for mgr in total_managers}
        for manager in managers:
            self._test_one_manager_object_for_manager(manager, user)
            self.assertIn(manager['id'], total_managers_ids)


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
            email='saulgoodman@rebase.io',
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
