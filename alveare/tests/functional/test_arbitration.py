import json
import time
import copy
import datetime
import unittest

from . import AlveareRestTestCase

class TestArbitrationResource(AlveareRestTestCase):

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

