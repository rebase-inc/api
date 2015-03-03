import json
import time
import unittest

from . import AlveareRestTestCase

class TestPerformance(AlveareRestTestCase):

    @unittest.skip('I just use this for back of the envelope benchmarking')
    def test_repeated_get(self):
        count = 100
        responses = []
        start = time.time()
        for _ in range(count):
            responses.append(self.client.get('work', headers={'X-Requested-With': 'XMLHttpRequest'}))
        elapsed = time.time() - start
        for response in responses:
            self.assertEqual(response.status_code, 200)
        raise Exception('{} requests per second'.format(count/elapsed))
