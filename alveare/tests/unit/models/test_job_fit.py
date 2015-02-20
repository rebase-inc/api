import unittest

from . import AlveareModelTestCase
from alveare.models import JobFit, TicketMatch
from alveare.common.mock import create_one_job_fit, create_one_candidate

class TestJobFit(AlveareModelTestCase):

    def test_create(self):
        job_fit = create_one_job_fit(self.db)
        self.db.session.commit()
        self.db.session.close()

        job_fits = JobFit.query.all()
        self.assertNotEqual(job_fits, [])

        job_fit = job_fits[0]
        self.assertNotEqual(job_fit.candidate, None)
        self.assertNotEqual(job_fit.ticket_matches, [])

    def test_delete(self):
        job_fit = create_one_job_fit(self.db)
        candidate = job_fit.candidate
        ticket_matches = job_fit.ticket_matches
        self.db.session.commit()

        self.db.session.delete(job_fit)
        self.db.session.commit()
        self.assertNotEqual(ticket_matches, [])
        self.assertNotEqual(candidate, None)

    @unittest.skip('need to fix cascading delete case')
    def test_delete_candidate(self):
        job_fit = create_one_job_fit(self.db)
        self.db.session.commit()

        self.db.session.delete(job_fit.candidate)
        self.db.session.commit()


    def test_empty_ticket_matches(self):
        candidate = create_one_candidate(self.db)
        skill_set = candidate.contractor.skill_set
        with self.assertRaises(ValueError):
            job_fit = JobFit(candidate, [])

    def test_incomplete_ticket_matches(self):
        candidate = create_one_candidate(self.db)
        skill_set = candidate.contractor.skill_set
        ticket_matches = []
        for bid_limit in candidate.ticket_set.bid_limits:
            ticket_matches.append(TicketMatch(skill_set, bid_limit.snapshot.ticket.skill_requirements, 100))
        ticket_matches.pop() # so we know we're missing one ticket_match
        with self.assertRaises(ValueError):
            job_fit = JobFit(candidate, ticket_matches)

