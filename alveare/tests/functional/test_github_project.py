from . import AlveareRestTestCase

url = 'github_projects/{}'.format

class TestGithubProjectResource(AlveareRestTestCase):

    def get_org(self):
        response = self.get_resource('organizations')
        self.assertIn('organizations', response)
        orgs = response['organizations']
        self.assertGreater(len(orgs), 1)
        return orgs[0]

    def create_project(self):
        # make the request data
        org = self.get_org()
        new_project = dict(organization=dict(id=org['id']), name='Falcon9')

        # create the resource
        response = self.post_resource('github_projects', new_project)

        # verify response
        self.assertIn('github_project', response)
        project = response['github_project']
        self.assertEqual(project['name'], new_project['name'])
        self.assertEqual(project['organization']['id'], org['id'])
        return project

    def test_create(self):
        self.login_admin()
        new_project = self.create_project()

        # verify by query
        project_id = new_project['id']
        response2 = self.get_resource(url(project_id))
        self.assertIn('github_project', response2)
        project2 = response2['github_project']
        self.assertEqual(project2['name'], new_project['name'])
        self.assertEqual(project2['organization'], new_project['organization'])

        # verify the created project is listed in the organization data
        org_response = self.get_resource('organizations/{}'.format(new_project['organization']['id']))
        self.assertIn('organization', org_response)
        org = org_response['organization']
        self.assertTrue(any(map(lambda project: project['id']==project_id, org['projects'])))

    def test_delete(self):
        self.login_admin()
        project = self.create_project()
        project_id = project['id']
        project_url = url(project_id)
        response = self.delete_resource(project_url)
        self.get_resource(project_url, 404)
        self.get_resource('code_repositories/{}'.format(project_id), 404)

    def test_put(self):
        self.login_admin()
        project = self.create_project()
        project_url = url(project['id'])
        project['name'] = 'Awesome Project Name!'

        response = self.put_resource(project_url, project)
        self.assertIn('github_project', response)
        updated_project = response['github_project']
        self.assertEqual(updated_project['name'], project['name'])

        # verify by query
        response2 = self.get_resource(project_url)
        self.assertIn('github_project', response2)
        project2 = response2['github_project']
        self.assertEqual(project2['name'], project['name'])

    def test_get_all(self):
        self.login_admin()
        project = self.create_project()
        project_id = project['id']

        response = self.get_resource('github_projects')
        self.assertIn('github_projects', response)
        projects = response['github_projects']
        self.assertTrue(any(map(lambda project: project['id']==project_id, projects)))
