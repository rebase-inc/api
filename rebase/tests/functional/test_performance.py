import json
import time
import unittest
import os
import sys
import cProfile
import pstats

sys.path.insert(0, os.path.expanduser('~/src/api'))
from rebase.tests.functional import RebaseRestTestCase

class TestPerformance(RebaseRestTestCase):

    @unittest.skip('I just use this for back of the envelope benchmarking')
    def test_repeated_get(self):
        self.login_admin()
        count = 40
        responses = []
        start = time.time()
        for _ in range(count):
            responses.append(self.client.get('work', headers={'X-Requested-With': 'XMLHttpRequest'}))
        elapsed = time.time() - start
        for response in responses:
            self.assertEqual(response.status_code, 200)
        raise Exception('{} requests per second'.format(count/elapsed))


if __name__ == '__main__':
    import logging
    logging.basicConfig()
    #logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    unittest.main()
