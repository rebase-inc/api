import unittest

from . import RebaseModelTestCase

from rebase import models
from rebase.common import mock
from rebase.common.utils import validate_query_fn
from rebase.tests.common.code_repository import (
    case_mgr_with_repo,
    case_cleared_contractor,
)

class TestCodeRepositoryModel(RebaseModelTestCase):

    def test_create(self):
        mock.create_one_project(self.db).code_repository
        self.db.session.commit()

    def test_delete(self):
        repo = mock.create_one_project(self.db).code_repository
        self.db.session.commit()

        self.delete_instance(repo)
        self.assertEqual(models.CodeRepository.query.get(repo.id), None)

    def test_delete_organization(self):
        repo = mock.create_one_project(self.db).code_repository
        self.db.session.commit()
        repo_id = repo.id
        self.db.session.delete(repo.project.organization)
        self.db.session.commit()

        queried_repo = models.CodeRepository.query.get(repo_id)
        self.assertFalse(queried_repo)

    @unittest.skip('CodeRepository model doesnt have any updatable fields yet')
    def test_update(self):
        new_code_repository = self.create_model(self.model)

    @unittest.skip('CodeRepository model doesnt have any creation fields yet')
    def test_bad_create(self):
        with self.assertRaises(ValueError):
            self.create_model(self.model, 'foo', 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 1234, 2)
        with self.assertRaises(ValueError):
            self.create_model(self.model, 123456789, 'foo')

    def test_as_mgr(self):
        validate_query_fn(self, models.CodeRepository, case_mgr_with_repo, models.CodeRepository.as_manager, 'manager', True, True, True, True)

    def test_as_contractor(self):
        validate_query_fn(self, models.CodeRepository, case_cleared_contractor, models.CodeRepository.as_contractor, 'contractor', False, False, False, True)

    def test_as_other_cleared_contractor(self):
        _, repo = case_cleared_contractor(self.db)
        user, _ = case_cleared_contractor(self.db)
        self.assertNotIn(repo, models.CodeRepository.as_contractor(user))
        self.assertFalse(repo.allowed_to_be_created_by(user))
        self.assertFalse(repo.allowed_to_be_modified_by(user))
        self.assertFalse(repo.allowed_to_be_deleted_by(user))
        self.assertFalse(repo.allowed_to_be_viewed_by(user))
