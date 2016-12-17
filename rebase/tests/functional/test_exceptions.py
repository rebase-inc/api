from copy import copy

from . import RebaseNoMockRestTestCase
from rebase.common.exceptions import (
    ServerError,
    ClientError,
    NotFoundError,
    InvalidGithubAccessToken,
    Forbidden,
    errors,
)
from rebase.common.schema import ValidationError
from rebase.models import (
    User,
)


class TestException(RebaseNoMockRestTestCase):
    def setUp(self):
        super().setUp()
        self.exception = None
        route = '/exception/raise'
        @self.app.route(self.prefix+route)
        def _raise():
            raise self.exception
        self.throw = lambda status: self.get_resource(route, expected_code=status)

    def validate(self, exception):
        with self.assertRaises(exception):
            response = self.throw(exception.status)
            self.assertEqual(response.data.message, exception.message)
            self.assertEqual(response.data.status, exception.status)

    def test_server_error(self):
        self.assertEqual(ServerError.status, 500)
        self.exception = ServerError()
        self.validate(ServerError)

    def test_client_error(self):
        self.assertEqual(ClientError.status, 400)
        self.exception = ClientError()
        self.validate(ClientError)

    def test_forbidden(self):
        self.assertEqual(Forbidden.status, 403)
        self.exception = Forbidden()
        self.validate(Forbidden)

    def test_not_found(self):
        self.assertEqual(NotFoundError.status, 404)
        self.exception = NotFoundError('FooBar', 31415926535)
        self.validate(NotFoundError)

    def test_invalid_github_access_token(self):
        self.assertEqual(InvalidGithubAccessToken.status, 500)
        rapha = User('Raphael Goyra', 'raphael@joinrebase.com', 'foo')
        self.exception = InvalidGithubAccessToken(rapha, 'rapha-on-github')
        self.validate(InvalidGithubAccessToken)

    def test_marshmallow_validation_error(self):
        from rebase.views.auth import deserializer
        rapha = User('Rapha', 'rapha@joinrebase.com', 'foo')
        self.db.session.add(rapha)
        self.db.session.commit()
        auth_form = {
            'user': {
                'id':       rapha.id,
                'email':    rapha.email,
            },
            'password': 'foo'
        }
        _form = copy(auth_form)
        del _form['password']
        with self.assertRaises(ValidationError) as context:
            auth_data = deserializer.load(_form).data
        self.assertEqual(context.exception.status, 400)
        self.assertTrue('password' in context.exception.data['message'])
