import json
import time
import copy
import datetime

from . import AlveareRestTestCase

class TestMediationResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('mediations')
        self.assertIn('mediations', response)
        self.assertIsInstance(response['mediations'], list)

    def test_get_one(self):
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

        self.assertEqual(mediation, {})

    def test_create_new(self):
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
        self.assertEqual(mediation, {})

    def test_update(self):
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


