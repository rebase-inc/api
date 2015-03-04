from . import AlveareRestTestCase

url = 'organizations/{}'.format

class TestOrganizationResource(AlveareRestTestCase):

    def test_get_all(self):
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

    def test_get_one(self):
        org = self.get_one()
        self.assertEqual(org['name'], 'Alveare')

    def test_post(self):
        organization_data = dict(name='SpaceX')
        response = self.post_resource('organizations', organization_data)
        self.assertIn('organization', response)

        organization = response['organization']
        self.assertEqual(organization['name'], organization_data['name'])

    def test_put(self):
        org = self.get_one()
        org['name'] = 'SpaceY'
        response = self.put_resource(url(org['id']), org)
        self.assertIn('organization', response)
        updated_org = response['organization']

        # verify
        response2 = self.get_resource(url(org['id']))
        self.assertIn('organization', response2)
        org2 = response2['organization']
        self.assertEqual(org2['name'], org['name'])


    def test_delete_one(self):
        org = self.get_one()

        self.delete_resource(url(org['id']))

        self.get_resource(url(org['id']), 404)
