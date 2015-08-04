from . import AlveareRestTestCase
from random import randrange
from rebase.common.utils import AlveareResource
from unittest import skip


class TestJobFitResource(AlveareRestTestCase):
    def setUp(self):
        self.job_fit_resource =         AlveareResource(self, 'JobFit')
        self.ticket_match_resource =    AlveareResource(self, 'TicketMatch')
        self.ticket_set_resource =      AlveareResource(self, 'TicketSet')
        self.ticket_snapshot_resource = AlveareResource(self, 'TicketSnapshot')
        self.nomination_resource =      AlveareResource(self, 'Nomination')
        self.bid_limit_resource =       AlveareResource(self, 'BidLimit')
        self.contractor_resource =      AlveareResource(self, 'Contractor')
        super().setUp()

    def test_get_one(self):
        self.login_admin()
        job_fit = self.job_fit_resource.get_any()
        self.assertTrue(job_fit) # mock should have created at least one ticket and its related JobFit object
        self.assertTrue(self.ticket_match_resource.get(job_fit['ticket_matches'][0]))
        self.assertTrue(self.nomination_resource.get(job_fit['nomination']))

    def test_create(self):
        self.login_admin()
        # find a nomination that does not have a JobFit yet (should find Andrew's nomination, as setup in the mock)
        nomination = next(filter(lambda _nomination: 'job_fit' not in _nomination, self.nomination_resource.get_all()))
        contractor_id = self.contractor_resource.get_any()['id']
        ticket_set = self.ticket_set_resource.get(nomination['ticket_set'])
        ticket_matches = []
        for bid_limit in ticket_set['bid_limits']:
            ticket_snapshot = self.ticket_snapshot_resource.get(self.bid_limit_resource.get(bid_limit)['ticket_snapshot'])
            ticket_id = ticket_snapshot['ticket']['id']
            try:
                ticket_match = self.ticket_match_resource.get(dict(
                    skill_requirement_id = ticket_id,
                    skill_set_id =          contractor_id
                ))
            except AssertionError as e:
                ticket_match = self.ticket_match_resource.create(
                    skill_requirement = {'id': ticket_id},
                    skill_set =         {'id': contractor_id},
                    score = randrange(100)
                )
            ticket_matches.append(self.ticket_match_resource.just_ids(ticket_match))
        nomination = self.nomination_resource.just_ids(nomination)
        self.job_fit_resource.create(
            nomination =        nomination,
            ticket_matches =    ticket_matches
        )

    def test_update(self):
        self.login_admin()
        job_fit = self.job_fit_resource.get_any()
        job_fit['score'] = job_fit['score'] + 10
        self.job_fit_resource.update(**job_fit) 

    def test_delete(self):
        self.login_admin()
        self.job_fit_resource.delete_any()

    def test_delete_nomination(self):
        self.login_admin()
        job_fit = self.job_fit_resource.get_any()
        self.nomination_resource.delete(**job_fit['nomination'])
        self.job_fit_resource.get(job_fit, 404)

    @skip('constraint is not enforced in the model')
    def test_delete_ticket_set(self):
        self.login_admin()
        job_fit = self.job_fit_resource.get_any()
        for ticket_match in job_fit['ticket_matches']:
            self.ticket_match_resource.delete(**ticket_match)
        self.job_fit_resource.get(job_fit, 404)

    def test_delete_organization(self):
        self.login_admin()
        job_fit = self.job_fit_resource.get_any()
        nomination = self.nomination_resource.get(job_fit['nomination'])
        ticket_set = self.ticket_set_resource.get(nomination['ticket_set'])

        bid_limit =         AlveareResource(self, 'BidLimit').get(ticket_set['bid_limits'][0])
        ticket_snapshot =   AlveareResource(self, 'TicketSnapshot').get(bid_limit['ticket_snapshot'])
        ticket =            AlveareResource(self, 'Ticket').get(ticket_snapshot['ticket'])
        project =           AlveareResource(self, 'Project').get(ticket['project'])
        org_resource =      AlveareResource(self, 'Organization')

        organization = org_resource.get(project['organization'])
        org_resource.delete(**organization)
        self.job_fit_resource.get(job_fit, 404)
