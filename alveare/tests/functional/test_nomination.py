from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip


class TestNominationResource(AlveareRestTestCase):
    def setUp(self):
        self.nomination_resource = AlveareResource(self, 'Nomination')
        self.contractor_resource = AlveareResource(self, 'Contractor')
        self.ticket_set_resource = AlveareResource(self, 'TicketSet')
        super().setUp()

    def test_get_one(self):
        nomination = self.nomination_resource.get_any()
        self.assertTrue(nomination) # mock should have created at least one ticket and its related Nomination object

    def test_create(self):
        self.nomination_resource.create(
            contractor = {'id': self.contractor_resource.get_any()['id']},
            ticket_set = {'id': self.ticket_set_resource.get_any()['id']},
        )

    def test_update(self):
        nomination = self.nomination_resource.get_any()
        nomination['approved_for_auction_id'] = nomination['ticket_set_id']
        self.nomination_resource.update(**nomination) 

    def test_delete(self):
        self.nomination_resource.delete_any()

    def test_delete_contractor(self):
        nomination = self.nomination_resource.get_any()
        contractor = self.contractor_resource.get(nomination['contractor'])
        self.contractor_resource.delete(contractor)
        self.nomination_resource.get(nomination, 404)

    def test_delete_ticket_set(self):
        nomination = self.nomination_resource.get_any()
        ticket_set = self.ticket_set_resource.get(nomination['ticket_set'])
        self.ticket_set_resource.delete(ticket_set)
        self.nomination_resource.get(nomination, 404)
