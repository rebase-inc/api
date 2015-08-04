import json
import time
import copy
import datetime
import unittest

from . import RebaseRestTestCase

class TestDebitResource(RebaseRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('debits')
        self.assertIn('debits', response)
        self.assertIsInstance(response['debits'], list)

    def test_get_one(self):
        self.login_admin()
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
        self.login_admin()
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

    def test_update(self):
        self.login_admin()
        response = self.get_resource('debits')
        debit_id = response['debits'][0]['id']

        response = self.get_resource('debits/{}'.format(debit_id))
        debit = response['debit']

        new_fields = dict(price = debit['price']*2, paid = not debit['price'])
        response = self.put_resource('debits/{}'.format(debit['id']), new_fields)
        debit.update(new_fields)
        self.assertEqual(debit, response['debit'])

    def test_delete(self):
        self.login_admin()
        pass
        user = dict(first_name='Hank', last_name='Schrader', email='hankschrader@rebase.io', password='theyreminerals')
        response = self.post_resource('users', user)
        user_id = response['user']['id']

        response = self.delete_resource('users/{}'.format(user_id))
        response = self.get_resource('users/{}'.format(user_id), expected_code=404)

