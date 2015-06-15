import unittest

from . import AlveareModelTestCase
from alveare.models import TicketSet
from alveare.common.mock import create_one_snapshot
from alveare.common.utils import validate_query_fn
from alveare.tests.common.ticket_set import (
    case_contractor,
    case_mgr,
    case_admin,
    case_anonymous,
)

class TestTicketSet(AlveareModelTestCase):

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
