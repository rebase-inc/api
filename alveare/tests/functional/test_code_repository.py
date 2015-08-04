from copy import copy

from . import AlveareRestTestCase, AlveareNoMockRestTestCase
from rebase.tests.common.code_repository import (
    case_mgr_with_repo,
    case_cleared_contractor,
)
from rebase.common.utils import AlveareResource, validate_resource_collection

class TestCodeRepository(AlveareNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.resource = AlveareResource(self, 'CodeRepository')
        self.project_resource = AlveareResource(self, 'Project')

    def test_as_manager(self):
        mgr_user, repo = case_mgr_with_repo(self.db)
        validate_resource_collection(self, mgr_user, [repo])
        repo_blob = self.resource.get(repo.id)
        project_blob = self.project_resource.get(repo.project.id)
        self.resource.update(**repo_blob)
        self.resource.delete(**repo_blob)
        new_repo = copy(repo_blob)
        del new_repo['id']
        new_repo['project'] = self.project_resource.just_ids(project_blob)
        self.resource.create(**new_repo)

    def test_as_contractor(self):
        contractor_user, repo = case_cleared_contractor(self.db)
        validate_resource_collection(self, contractor_user, [repo])
        repo_blob = self.resource.get(repo.id)
        self.resource.update(expected_status=401, **repo_blob)
        self.resource.delete(expected_status=401, **repo_blob)
        new_repo = copy(repo_blob)
        del new_repo['id']
        self.resource.create(expected_status=401, **new_repo)

    def test_as_anonymous(self):
        mgr_user, repo = case_mgr_with_repo(self.db)
        self.logout()
        self.assertFalse(self.resource.get_all(401))
