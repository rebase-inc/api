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
        self.assertEqual(github_project.organization.name, 'Rebase')
        self.assertNotEqual(github_project.code_repository, None)

    def test_delete(self):
        github_project = mock.create_one_github_project(self.db, project_name='api')
        self.db.session.commit()

        org_id = github_project.organization.id
        repo_id = github_project.code_repository.id

        self.assertEqual(github_project.name, 'api')
        self.assertEqual(github_project.organization.name, 'Rebase')
        self.assertNotEqual(github_project.code_repository, None)

        self.delete_instance(github_project)

        self.assertEqual(models.Organization.query.get(org_id).name, 'Rebase')
        self.assertEqual(models.CodeRepository.query.get(repo_id), None)

    #@unittest.skip('GithubProject model doesnt have any updatable fields yet')
    #def test_update(self):
        #return

    #@unittest.skip('GithubProject model doesnt have any creation fields yet')
    #def test_bad_create(self):
        #return

