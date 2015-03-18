from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestCandidateResource(AlveareRestTestCase):
    def setUp(self):
        self.candidate_resource = AlveareResource(self, 'Candidate')
        self.contractor_resource = AlveareResource(self, 'Contractor')
        self.ticket_set_resource = AlveareResource(self, 'TicketSet')
        super().setUp()

    def test_get_one(self):
        candidate = self.candidate_resource.get_any()
        self.assertTrue(candidate) # mock should have created at least one ticket and its related Candidate object

    def test_create(self):
        self.candidate_resource.create(
            contractor = {'id': self.contractor_resource.get_any()['id']},
            ticket_set = {'id': self.ticket_set_resource.get_any()['id']},
        )

    def test_update(self):
        candidate = self.candidate_resource.get_any()
        candidate['approved_for_auction_id'] = candidate['ticket_set_id']
        self.candidate_resource.update(**candidate) 

    def test_delete(self):
        self.candidate_resource.delete_any()

    def test_delete_contractor(self):
        candidate = self.candidate_resource.get_any()
        contractor = self.contractor_resource.get(candidate['contractor'])
        self.contractor_resource.delete(contractor)
        self.candidate_resource.get(candidate, 404)

    def test_delete_ticket_set(self):
        candidate = self.candidate_resource.get_any()
        ticket_set = self.ticket_set_resource.get(candidate['ticket_set'])
        self.ticket_set_resource.delete(ticket_set)
        self.candidate_resource.get(candidate, 404)
