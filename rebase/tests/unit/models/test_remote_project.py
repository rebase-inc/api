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
