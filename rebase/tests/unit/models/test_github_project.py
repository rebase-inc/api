import unittest

from sqlalchemy.orm.exc import ObjectDeletedError

from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock

class TestGithubProjectModel(RebaseModelTestCase):

    def test_create(self):
        github_project = mock.create_one_github_project(self.db, project_name='api')
        self.db.session.commit()

        self.assertEqual(github_project.name, 'api')
        self.assertNotEqual(github_project.work_repo, None)

    def test_delete(self):
        github_project = mock.create_one_github_project(self.db, project_name='api')
        self.db.session.commit()

        org_id = github_project.organization.id
        repo_id = (github_project.work_repo.code_repository_id, github_project.work_repo.project_id)

        self.assertEqual(github_project.name, 'api')
        self.assertNotEqual(github_project.code_repository, None)

        self.delete_instance(github_project)

        self.assertEqual(models.CodeRepository.query.get(repo_id), None)
