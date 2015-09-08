import unittest

from sqlalchemy.orm.exc import ObjectDeletedError

from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock

class TestRemoteProjectModel(RebaseModelTestCase):

    def test_create(self):
        remote_project = mock.create_one_remote_project(self.db, project_name='api')
        self.db.session.commit()

        self.assertEqual(remote_project.name, 'api')
        self.assertNotEqual(remote_project.code_repository, None)

    def test_delete(self):
        remote_project = mock.create_one_remote_project(self.db, project_name='api')
        self.db.session.commit()

        org_id = remote_project.organization.id
        repo_id = remote_project.code_repository.id

        self.assertEqual(remote_project.name, 'api')
        self.assertNotEqual(remote_project.code_repository, None)

        self.delete_instance(remote_project)

        self.assertEqual(models.CodeRepository.query.get(repo_id), None)

    def test_delete_organization(self):
        remote_project = mock.create_one_remote_project(self.db, project_name='Model S')
        self.db.session.commit()
        remote_project_id = remote_project.id

        self.db.session.delete(remote_project.organization)
        self.db.session.commit()

        queried_project = models.Project.query.get(remote_project_id)
        self.assertFalse(queried_project)

    def delete_project_with_ticket(self, make_ticket):
        remote_project = mock.create_one_remote_project(self.db, project_name='Model X')
        self.db.session.commit()
        remote_project_id = remote_project.id

        make_ticket(remote_project)

        self.db.session.delete(remote_project)
        self.db.session.commit()

        queried_project = models.Project.query.get(remote_project_id)
        self.assertFalse(queried_project)

    def make_internal_ticket(self, project):
        internal_ticket = self.create_model(
            models.InternalTicket,
            project,
            'Make batteries lighter',
            'Go from 1Kg/KWh to 0.7Kg/KWh at the same production price'
        )

    def make_github_ticket(self, project):
        github_ticket = self.create_model(
            models.GithubTicket,
            project,
            123
        )

    def test_delete_project_with_internal_tickets(self):
        self.delete_project_with_ticket(self.make_internal_ticket)

    def test_delete_project_with_github_tickets(self):
        self.delete_project_with_ticket(self.make_github_ticket)
