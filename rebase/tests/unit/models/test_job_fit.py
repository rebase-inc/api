import unittest

from . import RebaseModelTestCase
from rebase.models import JobFit, TicketMatch
from rebase.common.mock import create_one_job_fit, create_one_nomination

class TestJobFit(RebaseModelTestCase):

    def test_create(self):
        job_fit = create_one_job_fit(self.db)
        self.db.session.commit()
        self.db.session.close()

        job_fits = JobFit.query.all()
        self.assertNotEqual(job_fits, [])

        job_fit = job_fits[0]
        self.assertNotEqual(job_fit.nomination, None)
        all_ticket_matches = TicketMatch.query.all()
        self.assertNotEqual(all_ticket_matches, [])

        self.assertNotEqual(all_ticket_matches[0].job_fit, None)

    def test_delete(self):
        job_fit = create_one_job_fit(self.db)
        nomination = job_fit.nomination
        ticket_matches = job_fit.ticket_matches
        self.db.session.commit()

        self.db.session.delete(job_fit)
        self.db.session.commit()
        self.assertNotEqual(ticket_matches, [])
        self.assertNotEqual(nomination, None)

    def test_delete_nomination(self):
        job_fit = create_one_job_fit(self.db)
        self.db.session.commit()

        self.db.session.delete(job_fit.nomination)
        self.db.session.commit()

    def test_unrelate_nomination(self):
        job_fit = create_one_job_fit(self.db)
        self.db.session.commit()

        nomination = job_fit.nomination
        nomination.job_fit = None # unrelate JobFit from Nomination
        self.db.session.commit()

        # this really tests the 'delete-orphan' clause of the relationship
        # that is if one removes the 'delete-orphan' clause, this will fail
        self.assertEqual(JobFit.query.all(), [])

    def test_empty_ticket_matches(self):
        nomination = create_one_nomination(self.db)
        skill_set = nomination.contractor.skill_set
        with self.assertRaises(ValueError):
            job_fit = JobFit(nomination, [])

    def test_incomplete_ticket_matches(self):
        nomination = create_one_nomination(self.db)
        skill_set = nomination.contractor.skill_set
        ticket_matches = []
        for bid_limit in nomination.ticket_set.bid_limits:
            ticket_matches.append(TicketMatch(skill_set, bid_limit.ticket_snapshot.ticket.skill_requirement, 100))
        ticket_matches.pop() # so we know we're missing one ticket_match
        with self.assertRaises(ValueError):
            job_fit = JobFit(nomination, ticket_matches)

