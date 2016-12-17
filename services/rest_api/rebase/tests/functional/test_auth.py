from . import RebaseNoMockRestTestCase
from rebase.tests.common.auth import create_user

class TestAuth(RebaseNoMockRestTestCase):

    def test_logout(self):
        self.logout()
        self.post_resource('/auth', dict(), expected_code=401)
        self.get_resource('auctions', expected_code=401)
        self.get_resource('users', expected_code=401)

    def test_login(self):
        new_user = {
            'name': 'Joe Zeplummer',
            'email': 'joe@zeplummer.org',
            'password': 'foo'
        }
        # first, create new_user
        self.post_resource('users', new_user)

        # then login as new_user
        response = self.post_resource('/auth', dict(
            user=new_user,
            password=new_user['password'],
            role='contractor'
        ))

        self.assertIn('user', response)
        user = response['user']

        self.assertIn('current_role', user)
        current_role = user['current_role']

        self.assertEqual(current_role['type'], 'contractor')

        self.get_resource('users')
        response = self.get_resource('auctions')
        self.assertIn('auctions', response)

    def _role(self, current_role):
        user = create_user(self.db)
        logged_user = self.login(user.email, 'foo', role=current_role)
        self.assertEqual(current_role, logged_user['current_role']['type'])

    def test_contractor(self):
        self._role('contractor')

    def test_mgr(self):
        self._role('manager')

    def test_bogus_email(self):
        self.post_resource(
            '/auth',
            {
                'user': {'email': ''},
                'password': 'foo',
                'role': 'contractor'
            },
            expected_code = 401
        )

    def test_bogus_password(self):
        user = create_user(self.db)
        self.post_resource(
            '/auth',
            {
                'user': {'email': user.email},
                'password': '',
                'role': 'contractor'
            },
            expected_code = 401
        )

