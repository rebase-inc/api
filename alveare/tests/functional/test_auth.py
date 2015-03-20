from . import AlveareRestTestCase
from alveare.common.utils import AlveareResource
from unittest import skip

class TestAuth(AlveareRestTestCase):

    def test_login(self):
        # log out first (testware logs us in)
        response = self.post_resource('/auth', dict())

        self.get_resource('auctions', expected_code=401)
        user = self.get_resource('users')['users'][0]
        response = self.post_resource('/auth', dict(user=user))
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)
