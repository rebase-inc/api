import json
import time
import copy
import datetime
import unittest

from . import RebaseRestTestCase
from rebase.models import Arbitration

class TestArbitrationResource(RebaseRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('arbitrations')
        self.assertIn('arbitrations', response)
        self.assertIsInstance(response['arbitrations'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('arbitrations')
        arbitration_id = response['arbitrations'][0]['id']

        response = self.get_resource('arbitrations/{}'.format(arbitration_id))
        arbitration = response['arbitration']

        self.assertEqual(arbitration.pop('id'), arbitration_id)
        self.assertEqual(arbitration.pop('mediation'), arbitration_id)
        self.assertEqual(arbitration, {})

    def test_create_new(self):
        self.login_admin()
        ''' admin only '''
        response = self.get_resource('mediations')
        mediation = [m for m in response['mediations'] if 'arbitration' not in m][0]
        arbitration = dict(mediation={'id': mediation.get('id')})
        response = self.post_resource('arbitrations', arbitration)['arbitration']

        self.assertIsInstance(response.pop('id'), int)
        self.assertEqual(response.pop('mediation'), mediation.get('id'))
        self.assertEqual(response, {})

    @unittest.skip('arbitration has no updatable fields right now')
    def test_update(self):
        self.login_admin()
        ''' admin only '''
        pass

    def test_contractor_can_get_their_own(self):
        arbitration = Arbitration.query.first()
        contractor = arbitration.mediation.work.offer.contractor
        self.get_resource('arbitrations/{}'.format(arbitration.id), 401)
        self.login(contractor.user.email, 'foo')
        self.get_resource('arbitrations/{}'.format(arbitration.id))

        returned_arbitrations = self.get_resource('arbitrations')['arbitrations']
        returned_arbitration_ids = [a['id'] for a in returned_arbitrations]
        actual_arbitration_ids = []
        for work_offer in contractor.work_offers:
            if work_offer.work and work_offer.work.mediation_rounds:
                for mediation_round in work_offer.work.mediation_rounds:
                    if mediation_round.arbitration:
                        actual_arbitration_ids.append(mediation_round.arbitration.id)
        self.assertEqual(set(returned_arbitration_ids), set(actual_arbitration_ids))

        self.login_as_new_user()
        arbitrations = self.get_resource('arbitrations')['arbitrations']
        arbitration_ids = [a['id'] for a in arbitrations]
        self.assertNotIn(arbitration.id, arbitration_ids)

    def test_manager_of_auction_can_see_them(self):
        arbitration = Arbitration.query.first()
        manager = arbitration.mediation.work.offer.bid.auction.organization.managers[0]
        self.login(manager.user.email, 'foo')
        self.get_resource('arbitrations/{}'.format(arbitration.id))
        arbitrations = self.get_resource('arbitrations')['arbitrations']
        arbitration_ids = [a['id'] for a in arbitrations]
        self.assertIn(arbitration.id, arbitration_ids)

        self.login_as_new_user()
        self.get_resource('arbitrations/{}'.format(arbitration.id), 401)
        arbitrations = self.get_resource('arbitrations')['arbitrations']
        arbitration_ids = [a['id'] for a in arbitrations]
        self.assertNotIn(arbitration.id, arbitration_ids)

