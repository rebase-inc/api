import json
import time

from . import AlveareRestTestCase

class TestUserResource(AlveareRestTestCase):

    def test_foo(self):
        response = self.get_resource('users', expected_code = 200)
        self.assertIn('users', response)
