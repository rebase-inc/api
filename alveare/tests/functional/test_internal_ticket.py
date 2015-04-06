from unittest import skip
from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from alveare.common.mock import create_one_project
from alveare.models import (
    Project,
    Organization,
    Manager,
    Contractor,
    CodeClearance,
)

class TestInternalTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.internal_ticket_resource = AlveareResource(self, 'InternalTicket')
        self.project_resource = AlveareResource(self, 'Project')
        self.code_clearance_resource = AlveareResource(self, 'CodeClearance')
        super().setUp()

    def test_get_all_as_anonymous(self):
        internal_tickets = self.internal_ticket_resource.get_all(401)
        self.assertFalse(internal_tickets)

    def test_get_all_as_admin(self):
        self.login_admin()
        self.assertTrue(self.internal_ticket_resource.get_all())

    def _get_all_internal_projects_as_manager(self, user):
        return self.db.session.query(Project.id)\
            .filter(Project.type == 'project')\
            .join(Organization)\
            .join(Manager)\
            .filter(Manager.user == user)

    def _get_all_internal_projects_as_contractor(self, user):
        return self.db.session.query(Project.id)\
            .filter(Project.type == 'project')\
            .join(Project.clearances)\
            .join(CodeClearance.contractor)\
            .filter(Contractor.user == user)

    def _get_all(self, get_all_projects, user):
        project_ids = get_all_projects(user).all()
        project_ids = [prj[0] for prj in project_ids]
        self.assertTrue(project_ids)
        tickets = self.internal_ticket_resource.get_all()
        self.assertTrue(tickets)
        for ticket in tickets:
            self.assertIn('project', ticket)
            self.assertIn('id', ticket['project'])
            self.assertIn(ticket['project']['id'], project_ids)
            self.assertIn('discriminator', ticket)
            self.assertEqual(ticket['discriminator'], 'internal_ticket')

    def test_get_all_as_manager(self):
        self._get_all(
            self._get_all_internal_projects_as_manager,
            self.login_as_manager_only()
        )

    def test_get_all_as_contractor(self):
        user = self.login_as_contractor_only_with_clearance()
        self._get_all(
            self._get_all_internal_projects_as_contractor,
            self.login_as_contractor_only_with_clearance()
        )

    def _get_one(self):
        ticket = self.internal_ticket_resource.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertIn('id', ticket)
        self.assertIn('skill_requirement', ticket)
        self.assertIn('project', ticket)
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])
        return ticket

    def test_get_one_as_admin(self):
        self.login_admin()
        self._get_one()

    def test_get_one_as_manager(self):
        self.login_as_manager_only()
        ticket = self._get_one()

    def test_get_one_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        ticket = self._get_one()
        project = self.project_resource.get(ticket['project'])

    def test_get_invalid_id(self):
        self.login_admin()
        ticket = self.internal_ticket_resource.get(dict(
            id = 12341234
        ), 404)

    def _create(self, expected_status=201):
        project = AlveareResource(self, 'Project').get_any()
        self.internal_ticket_resource.create(
            expected_status,
            title = 'Foo',
            description = 'Bar',
            project = dict(id=project['id'])
        )

    def test_create_as_admin(self):
        self.login_admin()
        self._create()

    def test_create_as_manager(self):
        self.login_as_manager_only()
        self._create()

    def test_create_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        self._create(401)

    def test_bad_create(self):
        '''
            test marshmallow.exceptions.UnmarshallingError
        '''
        self.login_admin()
        project = AlveareResource(self, 'Project').get_any()
        ticket = dict(
            title = 'Foo',
            project = dict(id=project['id']),
        )
        error = self.post_resource(self.internal_ticket_resource.collection_url, ticket, 400)
        self.assertIn('status', error)
        self.assertEqual(error['status'], 400)
        self.assertIn('message', error)
        print(error['message'])

    def _update_one_ticket(self, expected_status=200):
        ticket = self.internal_ticket_resource.get_any()
        self.internal_ticket_resource.update(
            expected_status,
            id =            ticket['id'],
            title =         'Compelling title',
            description =   'Detailed description'
        )

    def test_update_as_admin(self):
        self.login_admin()
        self._update_one_ticket()

    def test_update_as_manager(self):
        self.login_as_manager_only()
        self._update_one_ticket()

    def test_update_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        self._update_one_ticket(401)

    def test_delete_as_admin(self):
        self.login_admin()
        self.internal_ticket_resource.delete_any()

    def test_delete_as_manager(self):
        self.login_as_manager_only()
        self.internal_ticket_resource.delete_any()

    def test_delete_as_contractor(self):
        self.login_as_contractor_only_with_clearance()
        ticket = self.internal_ticket_resource.get_any()
        self.internal_ticket_resource.delete(401, **ticket)

    def test_delete_project(self):
        self.login_admin()
        ticket = self.internal_ticket_resource.get_any()
        self.delete_resource('projects/{}'.format(ticket['project']['id']))
        self.get_resource(self.internal_ticket_resource.url(ticket), 404)
