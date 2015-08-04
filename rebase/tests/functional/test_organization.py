import unittest

from rebase.models import (
    Organization,
    Manager,
    User
)
from rebase.common.utils import RebaseResource
from . import RebaseRestTestCase

url = 'organizations/{}'.format

class TestOrganizationResource(RebaseRestTestCase):
    def setUp(self):
        self.org_resource =         RebaseResource(self, 'Organization')
        self.project_resource =     RebaseResource(self, 'Project')
        self.clearance_resource =   RebaseResource(self, 'CodeClearance')
        self.contractor_resource =  RebaseResource(self, 'Contractor')
        super().setUp()

    def test_get_all_anonymous(self):
        self.logout()
        self.assertFalse(self.org_resource.get_all(401))

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']
        self.assertGreater(len(orgs), 1)

    def get_one(self):
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']

        org_0 = orgs[0]

        org_response = self.get_resource(url(org_0['id']))
        self.assertIn('organization', org_response)
        return  org_response['organization']

    def test_every_org_has_at_least_one_manager(self):
        self.login_admin()
        orgs = self.org_resource.get_all()
        self.assertTrue(orgs)
        for org in orgs:
            with self.subTest(org_name=org['name']):
                self.assertTrue(org['managers'])

    def test_get_all_as_manager(self):
        user = self.login_as_manager_only()
        orgs = self.org_resource.get_all()
        self.assertTrue(orgs)
        for org in orgs:
            with self.subTest( org_name=org['name']):
                self.assertTrue(any(map(lambda mgr: mgr['user']['id'] == user.id, org['managers'])))

    def test_get_all_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        orgs = self.org_resource.get_all()
        self.assertTrue(orgs)
        for org in orgs:
            with self.subTest( org_name=org['name']):
                self.assertIn('projects', org)
                projects = org['projects']
                self.assertTrue(projects)
                for prj in projects:
                    project = self.project_resource.get(prj)
                    self.assertIn('clearances', project)
                    clearances = project['clearances']
                    self.assertTrue(clearances)
                    found_user = False
                    for clr in clearances:
                        clearance = self.clearance_resource.get(clr)
                        self.assertTrue(clearance)
                        self.assertIn('contractor', clearance)
                        contractor = self.contractor_resource.get(clearance['contractor'])
                        self.assertIn('user', contractor)
                        contractor_user = contractor['user']
                        self.assertIn('id', contractor_user)
                        found_user = contractor_user['id'] == user.id
                        if found_user:
                            break
                    self.assertTrue(found_user)

    def test_get_one_as_admin(self):
        self.login_admin()
        org = self.get_one()

    def test_get_one_as_manager(self):
        user = self.login_as_manager_only()
        an_org = user.roles.filter_by(type='manager').first().organization
        org = self.org_resource.get(dict(id=an_org.id))

    def test_get_one_as_user_only(self):
        user = self.login_as_no_role_user()
        any_org = Organization.query.first()
        self.org_resource.get(dict(id=any_org.id), 401)

    def test_get_one_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        org = self.org_resource.get_any()
        self.assertIn('projects', org)
        projects = org['projects']
        for prj in projects:
            self.assertIn('id', prj)
            project = self.project_resource.get(prj)
            self.assertIn('clearances', project)
            clearances = project['clearances']
            found_in_clearances = False
            for clr in clearances:
                clearance = self.clearance_resource.get(clr)
                self.assertIn('contractor', clearance)
                contractor = self.contractor_resource.get(clearance['contractor'])
                self.assertIn('user', contractor)
                contractor_user = contractor['user']
                self.assertIn('id', contractor_user)
                found_in_clearances = contractor_user['id'] == user.id
                if found_in_clearances:
                    break
        self.assertTrue(found_in_clearances)

    def test_post(self):
        user = self.login_as_no_role_user()
        organization_data = dict(name='SpaceX', user={'id':1})
        new_org = self.org_resource.create(
            validate = None,
            name='SpaceX',
            user={'id':user.id}
        )
        self.assertEqual(new_org['name'], 'SpaceX')
        self.assertEqual(new_org['managers'][0]['user']['id'], user.id)

    def test_modify_as_manager(self):
        org = Organization.query.first()
        user = org.managers[0].user
        self.login(user.email, 'foo')
        self.org_resource.update(
            id = org.id,
            name = org.name+' Bombed!'
        )

    def test_modify_as_user_only(self):
        self.login_as_no_role_user()
        org = Organization.query.first()
        self.org_resource.update(
            expected_status = 401,
            id = org.id,
            name = org.name+' Bombed!'
        )

    def test_delete_as_admin(self):
        self.login_admin()
        org = self.get_one()
        self.delete_resource(url(org['id']))
        self.get_resource(url(org['id']), 404)

    def test_delete_as_manager(self):
        org = Organization.query.first()
        user = org.managers[0].user
        self.login(user.email, 'foo')
        self.org_resource.delete(id = org.id) 

    def test_delete_as_non_manager(self):
        self.login_as_no_role_user()
        org = Organization.query.first()
        self.org_resource.delete(expected_status=401, id = org.id)
