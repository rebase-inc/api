import json
import time
import copy
import datetime

from . import AlveareRestTestCase

from alveare.models import Mediation

class TestMediationResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('mediations')
        self.assertIn('mediations', response)
        self.assertIsInstance(response['mediations'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('mediations')
        mediation_id = response['mediations'][0]['id']

        response = self.get_resource('mediations/{}'.format(mediation_id))
        mediation = response['mediation']
        self.assertIsInstance(mediation.pop('id'), int)
        self.assertIsInstance(mediation.pop('work'), int)
        self.assertIsInstance(mediation.pop('timeout'), str)
        self.assertIsInstance(mediation.pop('state'), str)

        if 'arbitration' in mediation:
            mediation.pop('arbitration')

        self.assertEqual(mediation.pop('comments'), [])
        self.assertEqual(mediation, {})

    def test_create_new(self):
        self.login_admin()
        ''' admin only '''
        response = self.get_resource('work')

        work = [work for work in response['work'] if not work['mediation']][0]

        mediation = dict(work={'id': work.get('id')})
        response = self.post_resource('mediations', mediation)
        mediation = response['mediation']

        self.assertIsInstance(mediation.pop('id'), int)
        self.assertIsInstance(mediation.pop('state'), str)
        self.assertIsInstance(mediation.pop('timeout'), str) #TODO: Actually check that this is a string
        self.assertEqual(mediation.pop('work'), work.get('id'))
        self.assertEqual(mediation.pop('comments'), [])
        self.assertEqual(mediation, {})

    def test_update(self):
        self.login_admin()
        ''' admin only '''
        response = self.get_resource('mediations')
        mediation_id = response['mediations'][0]['id']

        response = self.get_resource('mediations/{}'.format(mediation_id))
        mediation = response['mediation']
        new_state = dict(state = 'discussion' if mediation.get('state') != 'discussion' else 'waiting_for_client')
        if new_state.get('state') == 'waiting_for_client':
            new_state['dev_answer'] = 'in_progress'
        response = self.put_resource('mediations/{}'.format(mediation_id), new_state)
        mediation.update(new_state)
        self.assertEqual(mediation, response['mediation'])

    def test_contractor_can_get_their_own(self):
        mediation = Mediation.query.first()
        contractor = mediation.work.offer.contractor
        self.get_resource('mediations/{}'.format(mediation.id), 401)
        self.login(contractor.user.email, 'foo')
        self.get_resource('mediations/{}'.format(mediation.id))

        returned_mediations = self.get_resource('mediations')['mediations']
        returned_mediation_ids = [m['id'] for m in returned_mediations]
        actual_mediation_ids = []
        for work_offer in contractor.work_offers:
            if work_offer.work and work_offer.work.mediation_rounds:
                for mediation_round in work_offer.work.mediation_rounds:
                    actual_mediation_ids.append(mediation_round.id)
        self.assertEqual(set(returned_mediation_ids), set(actual_mediation_ids))

        self.login_as_new_user()
        mediations = self.get_resource('mediations')['mediations']
        mediation_ids = [m['id'] for m in mediations]
        self.assertNotIn(mediation.id, mediation_ids)

    def test_manager_of_auction_can_see_them(self):
        mediation = Mediation.query.first()
        manager = mediation.work.offer.bid.auction.organization.managers[0]
        self.login(manager.user.email, 'foo')
        self.get_resource('mediations/{}'.format(mediation.id))
        mediations = self.get_resource('mediations')['mediations']
        mediation_ids = [m['id'] for m in mediations]
        self.assertIn(mediation.id, mediation_ids)

        self.login_as_new_user()
        self.get_resource('mediations/{}'.format(mediation.id), 401)
        mediations = self.get_resource('mediations')['mediations']
        mediation_ids = [m['id'] for m in mediations]
        self.assertNotIn(mediation.id, mediation_ids)

