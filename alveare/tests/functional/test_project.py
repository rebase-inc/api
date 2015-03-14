from . import AlveareRestTestCase
from alveare.common.resource import AlveareResource
from unittest import skip


class TestProjectResource(AlveareRestTestCase):
    def setUp(self):
        self.r = AlveareResource(self, 'project')
        super().setUp()

    def test_get_one(self):
        project = self.r.get_any()
        self.assertTrue(project) # mock should have created at least one account
        self.assertTrue(project['id'])
        self.assertNotEqual(project['code_repository'], 0)

    def test_delete(self):
        project = self.r.delete_any()
        AlveareResource(self, 'code_repository').get(project['code_repository'], 404)

    def test_delete_organization(self):
        project = self.r.get_any()
        self.delete_resource('organizations/{}'.format(project['organization']['id']))
        self.get_resource(self.r.url(project), 404)

    def test_update(self):
        project = self.r.get_any()
        project['name'] = 'a better project name'
        self.r.update(**project)

    def test_add_and_remove_tickets(self):
        project = self.r.get_any()
        t = AlveareResource(self, 'internal_ticket')
        ticket = dict(
            title='Superb title',
            description='Lame description',
            project_id=project['id']
        )
        for i in range(50):
            ticket['title'] += ' #{}'.format(i)
            t.create(**ticket)
        queried_project = self.get('project', project['id'])
        self.assertTrue(queried_project)
        self.assertGreaterEqual(len(queried_project['tickets']), 50)

        # remove all tickets now
        for one_ticket in queried_project['tickets']:
            t.delete(one_ticket)

    def test_add_and_remove_code_clearance(self):
        contractor = AlveareResource(self, 'contractor').get_any()
        project = self.r.get_any()
        code_clearance = dict(pre_approved=True, project={'id': project['id']}, contractor={'id': contractor['id']})
        cc = AlveareResource(self, 'code_clearance')
        new_code_clearance = cc.create(**code_clearance)

        queried_project = self.r.get(project['id'])
        code_clearances = queried_project['clearances']
        self.assertTrue(code_clearances)
        queried_clearances = [c['id'] for c in queried_project['clearances']]
        self.assertIn(new_code_clearance['id'], queried_clearances)

        # now delete all code clearances
        for code_clearance in code_clearances:
            cc.delete(code_clearance)

        self.assertTrue(self.r.get(project['id']))

