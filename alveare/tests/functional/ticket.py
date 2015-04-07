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

class BaseTestTicketResource(AlveareRestTestCase):
    def setUp(self):
        self.ticket_resource = AlveareResource(self, 'Ticket')
        self.project_resource = AlveareResource(self, 'Project')
        self.code_clearance_resource = AlveareResource(self, 'CodeClearance')
        self.discriminator = 'ticket'
        self.check_discriminator = False
        self.allowed_project_types = ['project', 'github_project']
        super().setUp()

    def of_this_project_type(self, query):
        return query\
            .join(Project)\
            .filter(Project.type.in_(self.allowed_project_types))

    def login_as_contractor(self):
        return self.login_as_contractor_only_with_clearance(self.of_this_project_type)

    def with_project(self, query):
        return query\
            .join(Manager)\
            .join(Organization)\
            .join(Project)\
            .filter(Project.type.in_(self.allowed_project_types))

    def get_all_as_anonymous(self):
        tickets = self.ticket_resource.get_all(401)
        self.assertFalse(tickets)

    def get_all_as_admin(self):
        self.login_admin()
        self.assertTrue(self.ticket_resource.get_all())

    def _get_all_projects_as_manager(self, user):
        query = self.db.session.query(Project.id).filter(Project.type.in_(self.allowed_project_types))
        return query\
            .join(Organization)\
            .join(Manager)\
            .filter(Manager.user == user)

    def _get_all_projects_as_contractor(self, user):
        query = self.db.session.query(Project.id).filter(Project.type.in_(self.allowed_project_types))
        return query\
            .join(Project.clearances)\
            .join(CodeClearance.contractor)\
            .filter(Contractor.user == user)

    def _get_all(self, get_all_projects, user):
        project_ids = get_all_projects(user).all()
        project_ids = [prj[0] for prj in project_ids]
        self.assertTrue(project_ids)
        tickets = self.ticket_resource.get_all()
        self.assertTrue(tickets)
        for ticket in tickets:
            self.assertIn('project', ticket)
            self.assertIn('id', ticket['project'])
            self.assertIn(ticket['project']['id'], project_ids)
            self.assertIn('discriminator', ticket)
            if self.check_discriminator:
                self.assertEqual(ticket['discriminator'], self.discriminator)

    def get_all_as_manager(self):
        self._get_all(
            self._get_all_projects_as_manager,
            self.login_as_manager_only(self.with_project)
        )

    def get_all_as_contractor(self):
        self._get_all(
            self._get_all_projects_as_contractor,
            self.login_as_contractor()
        )

    def _get_one(self):
        ticket = self.ticket_resource.get_any()
        self.assertTrue(ticket) # mock should have created at least one account
        self.assertIn('id', ticket)
        self.assertIn('skill_requirement', ticket)
        self.assertIn('project', ticket)
        self.assertEqual(ticket['skill_requirement']['id'], ticket['id'])
        return ticket

    def get_one_as_admin(self):
        self.login_admin()
        self._get_one()

    def get_one_as_manager(self):
        self.login_as_manager_only(self.with_project)
        ticket = self._get_one()

    def get_one_as_contractor(self):
        self.login_as_contractor()
        ticket = self._get_one()
        project = self.project_resource.get(ticket['project'])

    def get_invalid_id(self):
        self.login_admin()
        ticket = self.ticket_resource.get(dict(
            id = 12341234
        ), 404)

    def _create(self, expected_status=201):
        project = self.project_resource.get_any()
        self.ticket_resource.create(
            expected_status,
            title = 'Foo',
            description = 'Bar',
            project = dict(id=project['id'])
        )

    def create_as_admin(self):
        self.login_admin()
        self._create()

    def create_as_manager(self):
        self.login_as_manager_only(self.with_project)
        self._create()

    def create_as_contractor(self):
        self.login_as_contractor()
        self._create(401)

    def bad_create(self):
        '''
            test marshmallow.exceptions.UnmarshallingError
        '''
        self.login_admin()
        project = self.project_resource.get_any()
        ticket = dict(
            title = 'Foo',
            project = dict(id=project['id']),
        )
        error = self.post_resource(self.ticket_resource.collection_url, ticket, 400)
        self.assertIn('status', error)
        self.assertEqual(error['status'], 400)
        self.assertIn('message', error)
        print(error['message'])

    def _update_one_ticket(self, expected_status=200):
        ticket = self.ticket_resource.get_any()
        self.ticket_resource.update(
            expected_status,
            id =            ticket['id'],
            title =         'Compelling title',
            description =   'Detailed description'
        )

    def update_as_admin(self):
        self.login_admin()
        self._update_one_ticket()

    def update_as_manager(self):
        self.login_as_manager_only(self.with_project)
        self._update_one_ticket()

    def update_as_contractor(self):
        self.login_as_contractor()
        self._update_one_ticket(401)

    def delete_as_admin(self):
        self.login_admin()
        self.ticket_resource.delete_any()

    def delete_as_manager(self):
        self.login_as_manager_only(self.with_project)
        self.ticket_resource.delete_any()

    def delete_as_contractor(self):
        self.login_as_contractor()
        ticket = self.ticket_resource.get_any()
        self.ticket_resource.delete(401, **ticket)

    def delete_project(self):
        self.login_admin()
        ticket = self.ticket_resource.get_any()
        self.delete_resource('projects/{}'.format(ticket['project']['id']))
        self.get_resource(self.ticket_resource.url(ticket), 404)
