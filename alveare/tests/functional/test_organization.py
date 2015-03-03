from . import AlveareRestTestCase

url = 'organizations/{}'.format

class TestOrganizationResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']
        self.assertGreater(len(orgs), 1)

    def test_get_one(self):
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']

        org_0 = orgs[0]

        org_response = self.get_resource(url(org_0['id']))
        self.assertIn('organization', org_response)
        org = org_response['organization']

        self.assertEqual(org['name'], 'Alveare')

    def test_delete_one(self):
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']
        self.assertGreater(len(orgs), 1)

        org_0 = orgs[0]

        self.delete_resource(url(org_0['id']))

        self.get_resource(url(org_0['id']), 404)
