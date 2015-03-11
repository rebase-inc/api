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

    def test_delete(self):
        self.r.delete_any()

    def test_delete_organization(self):
        project = self.r.get_any()
        self.delete_resource('organizations/{}'.format(project['organization_id']))
        self.get_resource(self.r.url(project), 404)

    def test_update(self):
        project = self.r.get_any()
        project['name'] = 'a better project name'
        self.r.update(**project) 

    def test_add_and_remote_tickets(self):
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

        # remote all tickets now
        for one_ticket in queried_project['tickets']:
            t.delete(one_ticket)

