from .project import BaseProjectTestCase
from rebase.common.utils import RebaseResource
from rebase.models import (
    Manager,
    Organization,
    Project,
    RemoteProject,
    GithubProject,
)

def with_at_least_one_github_project(query):
    ''' add-on filter to make sure the queried manager has at least one project to manage
    '''
    return query\
        .join(Manager)\
        .join(Organization)\
        .join(GithubProject)

class TestGithubProjectResource(BaseProjectTestCase):
    def setUp(self):
        super().setUp()
        self.project_resource = RebaseResource(self, 'GithubProject')

    def test_get_all_as_admin(self):
        self.get_all_as_admin()

    def test_get_all_as_manager(self):
        self.get_all_as_manager(with_at_least_one_github_project)

    def test_get_all_as_user_only(self):
        self.get_all_as_user_only()

    def test_get_all_as_contractor_with_clearance(self):
        self.get_all_as_contractor_with_clearance()

    def test_get_all_anonymous(self):
        self.get_all_anonymous()

    def test_get_one_as_admin(self):
        self.get_one_as_admin()

    def test_get_one_as_contractor(self):
        self.get_one_as_contractor()

    def test_create_anonymous(self):
        self.create_anonymous()

    def test_create_as_admin(self):
        self.create_as_admin()

    def test_create_as_manager(self):
        self.create_as_manager()

    def test_create_as_contractor(self):
        self.create_as_contractor()

    def test_delete_one_as_contractor(self):
        self.delete_one_as_contractor()

    def test_get_one_as_manager(self):
        self.get_one_as_manager(with_at_least_one_github_project)

    def test_get_one_anonymous(self):
        self.get_one_anonymous()

    def test_delete_as_admin(self):
        self.delete_as_admin()

    def test_delete_unauthorized(self):
        self.delete_unauthorized()

    def test_delete_organization_as_admin(self):
        self.delete_organization_as_admin()

    def test_update_unauthorized(self):
        self.update_unauthorized()

    def test_update_as_admin(self):
        self.update_as_admin()

    def test_update_as_manager(self):
        self.update_as_manager(with_at_least_one_github_project)

    def test_update_as_contractor(self):
        self.update_as_contractor()

    def test_add_and_remove_tickets(self):
        self.add_and_remove_tickets()

    def test_add_and_remove_code_clearance(self):
        self.add_and_remove_code_clearance()
