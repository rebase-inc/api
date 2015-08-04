import unittest

from . import RebaseModelTestCase
from rebase.models import TicketSet
from rebase.common.mock import create_one_snapshot
from rebase.common.utils import validate_query_fn
from rebase.tests.common.ticket_set import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
)

class TestTicketSet(RebaseModelTestCase):

    def test_contractor(self):
        validate_query_fn(
            self,
            TicketSet,
            case_contractor,
            TicketSet.query_by_user,
            False, False, False, True
        )

    def test_mgr(self):
        validate_query_fn(
            self,
            TicketSet,
            case_mgr,
            TicketSet.query_by_user,
            True, True, True, True
        )

    def test_admin(self):
        validate_query_fn(
            self,
            TicketSet,
            case_admin,
            TicketSet.query_by_user,
            True, True, True, True
        )

    def test_anonymous(self):
        validate_query_fn(
            self,
            TicketSet,
            case_anonymous,
            TicketSet.query_by_user,
            False, False, False, False
        )
