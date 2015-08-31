from . import RebaseRestTestCase
from rebase.common.utils import RebaseResource
from unittest import skip

class TestAuth(RebaseRestTestCase):

    def test_login(self):
        self.login_admin()
        response = self.post_resource('/auth', dict(), 401)
        self.get_resource('auctions', expected_code=401)
        self.get_resource('users', expected_code=401)

        new_user = {
            'first_name': 'Joe',
            'last_name': 'Zeplummer',
            'email': 'joe@zeplummer.org',
            'password': 'foo'
        }
        response = self.post_resource('users', new_user)
        response = self.post_resource('/auth', dict(user=new_user, password='foo'))
        self.get_resource('users')

        self.logout()
        self.get_resource('auctions', expected_code=401)

        self.login(new_user['email'], 'foo')
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)
