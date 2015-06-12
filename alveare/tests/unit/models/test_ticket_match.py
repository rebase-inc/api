from . import AlveareModelTestCase

from alveare.common.utils import validate_query_fn
from alveare.tests.common.ticket_match import (
    case_mgr,
    case_contractor,
    case_admin,
)
from alveare.models import TicketMatch
from alveare.common.mock import create_ticket_matches

class TestTicketMatch(AlveareModelTestCase):

    def test_create(self):
        ticket_matches = create_ticket_matches(self.db)
        self.db.session.commit()
        self.db.session.close()

        matches = TicketMatch.query.all()
        for match in matches:
            self.assertNotEqual(match.skill_requirement, None)
            self.assertNotEqual(match.skill_set, None)
            self.assertEqual(match.job_fit, None)

    def test_mgr(self):
        validate_query_fn(
            self,
            TicketMatch,
            case_mgr,
            TicketMatch.get_all,
            False, False, False, True
        )

    def test_contractor(self):
        validate_query_fn(
            self,
            TicketMatch,
            case_contractor,
            TicketMatch.get_all,
            False, False, False, False
        )


    def test_admin(self):
        user, resource = case_admin(self.db)
        expected_resources = [resource]
        resources = TicketMatch.query_by_user(user).all()
        self.assertEqual(expected_resources, resources)
        self.assertEqual(expected_resources, TicketMatch.query_by_user(user).all())
        self.assertEqual(True, bool(resource.allowed_to_be_created_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_modified_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_deleted_by(user)))
        self.assertEqual(True, bool(resource.allowed_to_be_viewed_by(user)))
