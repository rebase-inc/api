import unittest

from alveare.models import (
    Organization,
    Manager,
    User
)
from alveare.common.utils import AlveareResource
from . import AlveareRestTestCase

url = 'organizations/{}'.format

class TestOrganizationResource(AlveareRestTestCase):
    def setUp(self):
        self.org_resource = AlveareResource(self, 'Organization')
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

    def test_get_one_as_admin(self):
        self.login_admin()
        org = self.get_one()
        self.assertEqual(org['name'], 'Alveare')

    def test_get_one_as_manager(self):
        user = self.login_as_manager_only()
        an_org = user.roles.filter_by(type='manager').first().organization
        org = self.org_resource.get(dict(id=an_org.id))

    def test_get_one_as_user_only(self):
        user = self.login_as_no_role_user()
        print(user.roles.all())
        any_org = Organization.query.first()
        self.org_resource.get(dict(id=any_org.id), 401)

    def test_post(self):
        user = self.login_as_no_role_user()
        organization_data = dict(name='SpaceX', user={'id':1})
        response = self.post_resource('organizations', organization_data)
        self.assertIn('organization', response)

        organization = response['organization']
        self.assertEqual(organization['name'], organization_data['name'])
        id = organization['id']

        # verify
        response2 = self.get_resource(url(id))
        self.assertEqual(response2['organization']['name'], organization_data['name'])

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
            401,
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
        self.org_resource.delete(401, id = org.id)
