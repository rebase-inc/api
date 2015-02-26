import json
import time

from . import AlveareRestTestCase

class TestOrganizationResource(AlveareRestTestCase):

    def test_get_all(self):
        response = self.get_resource('organizations', expected_code = 200)
        self.assertIn('organizations', response)
