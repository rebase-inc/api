from . import RebaseRestTestCase
from rebase.common.utils import RebaseResource
from unittest import skip

class TestAuth(RebaseRestTestCase):

    def test_login(self):
        self.login_admin()
        user = self.get_resource('users')['users'][0]
        response = self.post_resource('/auth', dict(), 401)
        self.get_resource('auctions', expected_code=401)
        response = self.post_resource('/auth', dict(user=user, password='foo'))
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)

        self.logout()
        self.get_resource('auctions', expected_code=401)

        self.login(user['email'], 'foo')
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)
