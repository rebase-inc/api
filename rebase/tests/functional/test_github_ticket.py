from functools import partialmethod

from rebase.common.utils import ids, RebaseResource
from rebase.tests.common.ticket import (
    case_github_contractor,
    case_github_mgr,
    case_github_admin,
    case_github_admin_collection,
    case_github_anonymous,
    case_github_anonymous_collection,
)

from . import PermissionTestCase
from .ticket import BaseTestTicketResource


def _new_instance(github_ticket):
    return {
        'project': ids(github_ticket.project),
        'number': github_ticket.number+1
    }

class TestGithubTicket(PermissionTestCase):
    model = 'GithubTicket'
    _create = partialmethod(PermissionTestCase.create, new_instance=_new_instance)

    def test_contractor_collection(self):
        self.collection(case_github_contractor, 'contractor')

    def test_contractor_view(self):
        self.view(case_github_contractor, 'contractor', True)

    def test_contractor_modify(self):
        self.modify(case_github_contractor, 'contractor', False)

    def test_contractor_delete(self):
        self.delete(case_github_contractor, 'contractor', False)

    def test_contractor_create(self):
        self._create(case_github_contractor, 'contractor', False)

    def test_mgr_collection(self):
        self.collection(case_github_mgr, 'manager')

    def test_mgr_view(self):
        self.view(case_github_mgr, 'manager', True)

    def test_mgr_modify(self):
        self.modify(case_github_mgr, 'manager', True)

    def test_mgr_delete(self):
        self.delete(case_github_mgr, 'manager', True)

    def test_mgr_create(self):
        self._create(case_github_mgr, 'manager', True)

    def test_admin_collection(self):
        self.collection(case_github_admin_collection, 'manager')

    def test_admin_view(self):
        self.view(case_github_admin, 'manager', True)

    def test_admin_modify(self):
        self.modify(case_github_admin, 'manager', True)

    def test_admin_delete(self):
        self.delete(case_github_admin, 'manager', True)

    def test_admin_create(self):
        self._create(case_github_admin, 'manager', True)

    def test_anonymous_collection(self):
        self.collection(case_github_anonymous_collection, 'manager')

    def test_anonymous_view(self):
        self.view(case_github_anonymous, 'manager', False)

    def test_anonymous_modify(self):
        self.modify(case_github_anonymous, 'manager', False)

    def test_anonymous_delete(self):
        self.delete(case_github_anonymous, 'manager', False)

    def test_anonymous_create(self):
        self._create(case_github_anonymous, 'manager', False)
