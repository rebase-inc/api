from functools import partial

from rebase.common.utils import ids, RebaseResource
from rebase.tests.common.github_ticket import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
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
    _create = partial(PermissionTestCase.create, new_instance=_new_instance)

    def test_contractor_view(self):
        self.view(case_contractor, True)

    def test_contractor_modify(self):
        self.modify(case_contractor, False)

    def test_contractor_delete(self):
        self.delete(case_contractor, False)

    def test_contractor_create(self):
        TestGithubTicket._create(self, case_contractor, False)

    def test_mgr_view(self):
        self.view(case_mgr, True)

    def test_mgr_modify(self):
        self.modify(case_mgr, True)

    def test_mgr_delete(self):
        self.delete(case_mgr, True)

    def test_mgr_create(self):
        TestGithubTicket._create(self, case_mgr, True)

    def test_admin_view(self):
        self.view(case_admin, True)

    def test_admin_modify(self):
        self.modify(case_admin, True)

    def test_admin_delete(self):
        self.delete(case_admin, True)

    def test_admin_create(self):
        TestGithubTicket._create(self, case_admin, True)

    def test_anonymous_view(self):
        self.view(case_anonymous, False)

    def test_anonymous_modify(self):
        self.modify(case_anonymous, False)

    def test_anonymous_delete(self):
        self.delete(case_anonymous, False)

    def test_anonymous_create(self):
        TestGithubTicket._create(self, case_anonymous, False)
