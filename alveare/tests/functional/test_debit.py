import json
import time
import copy
import datetime
import unittest

from . import AlveareRestTestCase

class TestDebitResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('debits')
        self.assertIn('debits', response)
        self.assertIsInstance(response['debits'], list)

    def test_get_one(self):
        response = self.get_resource('debits')
        debit_id = response['debits'][0]['id']

        response = self.get_resource('debits/{}'.format(debit_id))
        debit = response['debit']

        self.assertEqual(debit.pop('id'), debit_id)
        self.assertIsInstance(debit.pop('price'), int)
        self.assertIsInstance(debit.pop('paid'), bool)
        self.assertIsInstance(debit.pop('work'), int)
        self.assertEqual(debit, {})

    def test_create_new(self):
        ''' admin only '''
        response = self.get_resource('work')
        work = [w for w in response['work'] if 'debit' not in w][0]
        debit = dict(work={'id': work.get('id')}, price=1234)
        response = self.post_resource('debits', debit)['debit']

        self.assertIsInstance(response.pop('id'), int)
        self.assertEqual(response.pop('work'), work.get('id'))
        self.assertEqual(response.pop('price'), 1234)
        self.assertEqual(response.pop('paid'), False)
        self.assertEqual(response, {})

    #@unittest.skip('debit has no updatable fields right now')
    #def test_update(self):
        #''' admin only '''
        #pass

