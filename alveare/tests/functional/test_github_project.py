from . import AlveareRestTestCase

url = 'github_projects/{}'.format

class TestGithubProjectResource(AlveareRestTestCase):

    def get_org(self):
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']
        self.assertGreater(len(orgs), 1)
        return orgs[0]

    def test_create(self):
        # make the request data
        org = self.get_org()
        new_project = dict(organization_id=org['id'], name='MaximumDough')

        # create the resource
        response = self.post_resource('github_projects', new_project)

        # verify response
        self.assertIn('github_project', response)
        project = response['github_project']
        self.assertEqual(project['name'], new_project['name'])
        self.assertEqual(project['organization_id'], org['id'])

        # verify by query
        project_id = project['id']
        response2 = self.get_resource(url(project_id))
        self.assertIn('github_project', response2)
        project2 = response2['github_project']
        self.assertEqual(project2['name'], new_project['name'])
        self.assertEqual(project2['organization_id'], org['id'])
