from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestProjectResource(AlveareRestTestCase):
    def setUp(self):
        self.project_resource = AlveareResource(self, 'Project')
        super().setUp()

    def test_get_one(self):
        project = self.project_resource.get_any()
        self.assertTrue(project) # mock should have created at least one account
        self.assertTrue(project['id'])
        self.assertNotEqual(project['code_repository'], 0)

    def test_delete(self):
        project = self.project_resource.delete_any()
        AlveareResource(self, 'CodeRepository').get(project['code_repository'], 404)

    def test_delete_organization(self):
        project = self.project_resource.get_any()
        self.delete_resource('organizations/{}'.format(project['organization']['id']))
        self.get_resource(self.project_resource.url(project), 404)

    def test_update(self):
        project = self.project_resource.get_any()
        project['name'] = 'a better project name'
        self.project_resource.update(**project)

    def test_add_and_remove_tickets(self):
        project = self.project_resource.get_any()
        t = AlveareResource(self, 'InternalTicket')
        ticket = dict(
            description='Lame description',
            project = dict(id=project['id'])
        )
        for i in range(50):
            ticket['title'] = 'Superb title #{}'.format(i)
            t.create(**ticket)
        queried_project = self.get_resource('projects/{id}'.format(**project))['project']
        self.assertTrue(queried_project)
        self.assertGreaterEqual(len(queried_project['tickets']), 50)

        # remove all tickets now
        for one_ticket in queried_project['tickets']:
            t.delete(one_ticket)

    def test_add_and_remove_code_clearance(self):
        contractor = AlveareResource(self, 'Contractor').get_any()
        project = self.project_resource.get_any()
        code_clearance = dict(pre_approved=True, project={'id': project['id']}, contractor={'id': contractor['id']})
        cc = AlveareResource(self, 'CodeClearance')
        new_code_clearance = cc.create(**code_clearance)

        queried_project = self.project_resource.get(project['id'])
        code_clearances = queried_project['clearances']
        self.assertTrue(code_clearances)
        queried_clearances = [c['id'] for c in queried_project['clearances']]
        self.assertIn(new_code_clearance['id'], queried_clearances)

        # now delete all code clearances
        for code_clearance in code_clearances:
            cc.delete(code_clearance)

        self.assertTrue(self.project_resource.get(project['id']))

