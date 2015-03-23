import json
import time
import copy
import datetime
import unittest

from . import AlveareRestTestCase

class TestCreditResource(AlveareRestTestCase):

    def test_get_all(self):
        self.login_admin()
        response = self.get_resource('credits')
        self.assertIn('credits', response)
        self.assertIsInstance(response['credits'], list)

    def test_get_one(self):
        self.login_admin()
        response = self.get_resource('credits')
        credit_id = response['credits'][0]['id']

        response = self.get_resource('credits/{}'.format(credit_id))
        credit = response['credit']

        self.assertEqual(credit.pop('id'), credit_id)
        self.assertIsInstance(credit.pop('price'), int)
        self.assertIsInstance(credit.pop('paid'), bool)
        self.assertIsInstance(credit.pop('work'), int)
        self.assertEqual(credit, {})

    def test_create_new(self):
        self.login_admin()
        ''' admin only '''
        response = self.get_resource('work')
        work = [w for w in response['work'] if 'credit' not in w][0]
        credit = dict(work={'id': work.get('id')}, price=1234)
        response = self.post_resource('credits', credit)['credit']

        self.assertIsInstance(response.pop('id'), int)
        self.assertEqual(response.pop('work'), work.get('id'))
        self.assertEqual(response.pop('price'), 1234)
        self.assertEqual(response.pop('paid'), False)
        self.assertEqual(response, {})

    def test_update(self):
        self.login_admin()
        response = self.get_resource('credits')
        credit_id = response['credits'][0]['id']

        response = self.get_resource('credits/{}'.format(credit_id))
        credit = response['credit']

        new_fields = dict(price = credit['price']*2, paid = not credit['price'])
        response = self.put_resource('credits/{}'.format(credit['id']), new_fields)
        credit.update(new_fields)
        self.assertEqual(credit, response['credit'])

    def test_delete(self):
        self.login_admin()
        pass
        user = dict(first_name='Hank', last_name='Schrader', email='hankschrader@alveare.io', password='theyreminerals')
        response = self.post_resource('users', user)
        user_id = response['user']['id']

        response = self.delete_resource('users/{}'.format(user_id))
        response = self.get_resource('users/{}'.format(user_id), expected_code=404)

