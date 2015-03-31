from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from alveare.models import (
    Project,
    Manager,
    User,
)
from unittest import skip


class TestProjectResource(AlveareRestTestCase):
    def setUp(self):
        self.project_resource = AlveareResource(self, 'Project')
        super().setUp()

    def test_get_all(self):
        self.login_admin()
        projects = self.project_resource.get_all()

    def test_get_all_anonymous(self):
        self.get_resource('projects', 401)

    def test_get_one(self):
        self.login_admin()
        project = self.project_resource.get_any()
        self.assertTrue(project) # mock should have created at least one account
        self.assertTrue(project['id'])
        self.assertNotEqual(project['code_repository'], 0)

        project['id'] += 123123423445
        self.project_resource.get(project, 404)

    def test_get_one_unauthorized(self):
        project = Project.query.first()
        managers = project.organization.managers
        user = User.query.filter(~User.id.in_([manager.user.id for manager in managers])).first()
        self.login(user.email, 'foo')
        self.project_resource.get(dict(id=project.id), 401)

    def test_delete(self):
        self.login_admin()
        project = self.project_resource.delete_any()
        AlveareResource(self, 'CodeRepository').get(project['code_repository'], 404)

    def test_delete_unauthorized(self):
        self.login_admin()
        project = self.project_resource.get_any()
        self.logout()
        self.login_as_new_user()
        self.project_resource.delete(401, **project)
        self.login_admin()
        self.project_resource.delete(**project)

    def test_delete_organization(self):
        self.login_admin()
        project = self.project_resource.get_any()
        self.delete_resource('organizations/{}'.format(project['organization']['id']))
        self.get_resource(self.project_resource.url(project), 404)

    def test_update(self):
        self.login_admin()
        project = self.project_resource.get_any()
        project['name'] = 'a better project name'
        self.project_resource.update(**project)

    def test_update_unauthorized(self):
        project = Project.query.first()
        unauthorized_user = User.query\
            .join(Manager)\
            .filter(Manager.organization != project.organization)\
            .filter(~User.admin)\
            .first()
        self.project_resource.update(401, id=project.id, name=project.name+' Bombed!')

    def test_add_and_remove_tickets(self):
        self.login_admin()
        project = self.project_resource.get_any()
        internal_ticket_resource = AlveareResource(self, 'InternalTicket')
        ticket_resource = AlveareResource(self, 'Ticket')
        ticket = dict(
            description='Lame description',
            project = dict(id=project['id'])
        )
        for i in range(50):
            ticket['title'] = 'Superb title #{}'.format(i)
            internal_ticket_resource.create(**ticket)
        queried_project = self.get_resource('projects/{id}'.format(**project))['project']
        self.assertTrue(queried_project)
        self.assertGreaterEqual(len(queried_project['tickets']), 50)

        # remove all tickets now
        for one_ticket in queried_project['tickets']:
            ticket_resource.delete(**one_ticket)

    def test_add_and_remove_code_clearance(self):
        self.login_admin()
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
            cc.delete(**code_clearance)

        self.assertTrue(self.project_resource.get(project['id']))

