import json
import time
import copy

from . import AlveareRestTestCase

class TestWorkResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('work')
        self.assertIn('work', response)
        self.assertIsInstance(response['work'], list)

    def test_get_one(self):
        response = self.get_resource('work')
        work_id = response['work'][0]['id']

        response = self.get_resource('work/{}'.format(work_id))
        work = response['work']
        self.assertIsInstance(work.pop('id'), int)
        self.assertIsInstance(work.pop('state'), str)
        self.assertIsInstance(work.pop('review'), dict)
        self.assertIn('state', work.pop('mediation')[0])

