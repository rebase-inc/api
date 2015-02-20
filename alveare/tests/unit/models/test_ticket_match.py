import unittest

from . import AlveareModelTestCase
from alveare.models import TicketMatch
from alveare.common.mock import create_ticket_matches

class TestCandidate(AlveareModelTestCase):

    def test_create(self):
        ticket_matches = create_ticket_matches(self.db)
        self.db.session.commit()
        self.db.session.close()

        matches = TicketMatch.query.all()
        for match in matches:
            self.assertNotEqual(match.skill_requirements, None)
            self.assertNotEqual(match.skill_set, None)
            self.assertEqual(match.job_fit, None)
