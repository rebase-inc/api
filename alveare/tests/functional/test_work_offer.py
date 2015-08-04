import json
import time
import copy

from . import AlveareRestTestCase
from rebase.models import Contractor, TicketSnapshot, WorkOffer

class TestWorkOfferResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('work_offers')
        self.assertIn('work_offers', response)
        self.assertIsInstance(response['work_offers'], list)
        self.assertIsInstance(response['work_offers'][0]['ticket_snapshot'], int)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('work_offers')
        work_offer_id = response['work_offers'][0]['id']

        response = self.get_resource('work_offers/{}'.format(work_offer_id))
        work_offer = response['work_offer']

        self.assertIsInstance(work_offer.pop('id'), int)
        self.assertIsInstance(work_offer.pop('work', 1), int)
        self.assertIsInstance(work_offer.pop('price'), int)
        self.assertIsInstance(work_offer.pop('ticket_snapshot'), int)
        self.assertEqual(work_offer, {})

    def test_create_new(self):
        self.login_admin()
        snapshot = self.get_resource('ticket_snapshots')['ticket_snapshots'][0]
        contractor = self.get_resource('contractors')['contractors'][0]

        response = self.post_resource('work_offers', dict(ticket_snapshot=snapshot, price=7890, contractor=contractor))
        work_offer = response['work_offer']
        {'work_offer': {'id': 29, 'price': 7890, 'ticket_snapshot': 1}}

        self.assertIsInstance(work_offer.pop('id'), int)
        self.assertEqual(work_offer.pop('price'), 7890)
        self.assertEqual(work_offer.pop('ticket_snapshot'), snapshot['id'])
        self.assertEqual(work_offer, {})

    def test_update(self):
        self.login_admin()
        response = self.get_resource('work_offers')
        work_offer_id = response['work_offers'][0]['id']

        response = self.get_resource('work_offers/{}'.format(work_offer_id))
        work_offer = response['work_offer']

        new_fields = dict(price = work_offer['price']*2)
        response = self.put_resource('work_offers/{}'.format(work_offer['id']), new_fields)
        work_offer.update(new_fields)
        self.assertEqual(work_offer, response['work_offer'])

    def test_delete(self):
        self.login_admin()
        response = self.get_resource('work_offers')
        work_offer_id = response['work_offers'][0]['id']

        self.delete_resource('work_offers/{}'.format(work_offer_id))
        self.get_resource('work_offers/{}'.format(work_offer_id), expected_code=404)

    def test_contractor_can_get_their_own(self):
        contractor = Contractor.query.first()
        snapshot = TicketSnapshot.query.first()
        work_offer_data = dict(
            ticket_snapshot= dict(id = snapshot.id),
            contractor = dict(id = contractor.id),
            price = 9999
        )
        self.login(contractor.user.email, 'foo')
        new_work_offer = self.post_resource('work_offers', work_offer_data)['work_offer']
        self.get_resource('work_offers/{id}'.format(**new_work_offer))

        work_offers = self.get_resource('work_offers')['work_offers']
        work_offer_ids = [wo['id'] for wo in work_offers]
        self.assertIn(new_work_offer['id'], work_offer_ids)

        self.login_as_new_user()
        self.get_resource('work_offers/{id}'.format(**new_work_offer), 401)

        work_offers = self.get_resource('work_offers')['work_offers']
        work_offer_ids = [wo['id'] for wo in work_offers]
        self.assertNotIn(new_work_offer['id'], work_offer_ids)

    def test_manager_of_auction_can_see_them(self):
        work_offer = WorkOffer.query.filter(WorkOffer.bid != None).first()
        manager = work_offer.bid.auction.organization.managers[0]

        self.login(manager.user.email, 'foo')
        self.get_resource('work_offers/{}'.format(work_offer.id))
        work_offers = self.get_resource('work_offers')['work_offers']
        work_offer_ids = [wo['id'] for wo in work_offers]
        self.assertIn(work_offer.id, work_offer_ids)

        self.login_as_new_user()
        self.get_resource('work_offers/{}'.format(work_offer.id), 401)
        work_offers = self.get_resource('work_offers')['work_offers']
        work_offer_ids = [wo['id'] for wo in work_offers]
        self.assertNotIn(work_offer.id, work_offer_ids)
