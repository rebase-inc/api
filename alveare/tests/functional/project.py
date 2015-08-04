from . import AlveareRestTestCase
from rebase.common.utils import AlveareResource
from rebase.models import (
    Project,
    Manager,
    User,
    CodeClearance,
    Organization,
)
from unittest import skip


class BaseProjectTestCase(AlveareRestTestCase):
    def setUp(self):
        self.project_resource = AlveareResource(self, 'Project')
        self.org_resource = AlveareResource(self, 'Organization')
        super().setUp()

    def get_all_as_admin(self):
        self.login_admin()
        self.assertTrue(self.project_resource.get_all())

    def get_all_as_manager(self, with_at_least_one_project):
        user = self.login_as_manager_only(with_at_least_one_project)
        projects = self.project_resource.get_all()
        self.assertTrue(projects)
        for project in projects:
            self.assertIn('organization', project)
            org = self.org_resource.get(project['organization'])
            self.assertTrue(any(map(lambda mgr: mgr['user']['id']==user.id, org['managers'])))

    def get_all_as_user_only(self):
        self.login_as_no_role_user()
        self.assertFalse(self.project_resource.get_all())

    def get_all_as_contractor_with_clearance(self):
        user = self.login_as_contractor_only_with_clearance()
        contractor_id = user.roles[0].id
        clearances = self.db.session.query(CodeClearance.id).filter_by(contractor_id=contractor_id).all()
        clearances = [clr[0] for clr in clearances]
        self.assertTrue(clearances)
        projects = self.project_resource.get_all()
        self.assertTrue(projects)
        for project in projects:
            found_self = False
            for clr in project['clearances']:
                if clr['id'] in clearances:
                    found_self = True # means this user has indeed the right to view this project
                    break
            self.assertTrue(found_self)

    def get_all_anonymous(self):
        self.get_resource('projects', 401)

    def get_one_as_admin(self):
        self.login_admin()
        project = self.project_resource.get_any()
        self.assertTrue(project) # mock should have created at least one account
        self.assertTrue(project['id'])
        self.assertNotEqual(project['code_repository'], 0)
        project['id'] += 123123423445
        self.project_resource.get(project, 404)

    def _get_one(self):
        projects = self.project_resource.get_all()
        self.assertTrue(projects)
        for project in projects:
            self.project_resource.get(project)

    def get_one_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        self._get_one()

    def create_anonymous(self):
        org = Organization.query.first()
        self.project_resource.create(
            expected_status=401,
            name='fancy',
            organization= {'id': org.id}
        )

    def create_as_admin(self):
        user = self.login_admin()
        org = Organization.query.first()
        self.project_resource.create(
            name='fancy',
            organization= {'id': org.id}
        )

    def create_as_manager(self):
        user = self.login_as_manager_only()
        org = user.roles[0].organization
        self.project_resource.create(
            name='fancy',
            organization= {'id': org.id}
        )

    def create_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        org = user.roles[0].clearances[0].project.organization
        self.project_resource.create(
            expected_status=401,
            name='fancy',
            organization= {'id': org.id}
        )

    def delete_one_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        projects = self.project_resource.get_all()
        self.assertTrue(projects)
        for project in projects:
            self.project_resource.delete(expected_status=401, **project)

    def get_one_as_manager(self, with_at_least_one_project):
        user = self.login_as_manager_only(with_at_least_one_project)
        self._get_one()

    def get_one_anonymous(self):
        project = Project.query.first()
        self.project_resource.get(dict(id=project.id), 401)

    def delete_as_admin(self):
        self.login_admin()
        project = self.project_resource.delete_any()
        AlveareResource(self, 'CodeRepository').get(project['code_repository'], 404)

    def delete_unauthorized(self):
        self.login_admin()
        project = self.project_resource.get_any()
        self.logout()
        self.login_as_new_user()
        self.project_resource.delete(expected_status=401, **project)
        self.login_admin()
        self.project_resource.delete(**project)

    def delete_organization_as_admin(self):
        self.login_admin()
        project = self.project_resource.get_any()
        self.delete_resource('organizations/{}'.format(project['organization']['id']))
        self.get_resource(self.project_resource.url(project), 404)

    def update_unauthorized(self):
        project = Project.query.first()
        unauthorized_user = User.query\
            .join(Manager)\
            .filter(Manager.organization != project.organization)\
            .filter(~User.admin)\
            .first()
        self.project_resource.update(expected_status=401, id=project.id, name=project.name+' Bombed!')

    def _update_as_manager(self, expected_status):
        projects = self.project_resource.get_all()
        self.assertTrue(projects)
        for project in projects:
            project['name'] += ' tagged!'
            self.project_resource.update(expected_status=expected_status, **project)

    def update_as_admin(self):
        self.login_admin()
        self._update_as_manager(200)

    def update_as_manager(self, with_at_least_one_project):
        self.login_as_manager_only(with_at_least_one_project)
        self._update_as_manager(200)

    def update_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        self._update_as_manager(401)

    def add_and_remove_tickets(self):
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

    def add_and_remove_code_clearance(self):
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

