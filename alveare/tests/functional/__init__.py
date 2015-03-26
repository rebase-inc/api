import json
import datetime
import unittest

from alveare import models, create_app
from alveare.common.database import DB
from alveare.common.mock import create_the_world, create_admin_user

class AlveareRestTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(DB)
        self.db = DB

        # not really sure why this is required
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        self.db.create_all()
        self.db.session.commit()

        create_the_world(self.db)
        self.admin_user = create_admin_user(self.db, password='admin')
        self.db.session.commit()

        self.addCleanup(self.cleanup)

    def login_admin(self):
        self.post_resource('/auth', { 'user': {'email': self.admin_user.email}, 'password': 'admin'})

    def login(self, email, password):
        return self.post_resource('/auth', { 'user': {'email': email}, 'password': password})

    def logout(self):
        self.get_resource('/auth')

    def login_as_new_user(self):
        new_user = models.User.query.filter(~models.User.roles.any() & ~models.User.admin).first()
        self.post_resource('/auth', {'user': {'id': new_user.id, 'email': new_user.email}, 'password': 'foo' } )

    def cleanup(self):
        try:
            self.logout()
        except:
            pass
        self.db.session.remove()
        self.db.drop_all()
        self.db.get_engine(self.app).dispose()
        self.app_context.pop()

    def get_resource(self, url, expected_code=200):
        error_msg = 'Expected {}, got {}. Data: {}'
        # the header is required because of flask jsonify
        # see http://stackoverflow.com/questions/16908943/flask-display-json-in-a-neat-way
        response = self.client.get(url, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(response.status_code,
                         expected_code,
                         error_msg.format(expected_code, response.status_code, 'GET to {} failed: {}'.format(url, response.data))
                         )
        self.assertEqual(response.headers['Content-Type'], 'application/json',
            error_msg.format('application/json', response.headers['Content-Type'], response.data))
        return json.loads(response.data.decode('utf-8'))

    def post_resource(self, url, data, expected_code = 201):
        error_msg = 'Expected {}, got {}. Data: {}'
        response = self.client.post(url, data = json.dumps(data),
                headers={'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, expected_code,
            error_msg.format(expected_code, response.status_code, 'POST to {} failed: {}'.format(url, response.data)))
        self.assertEqual(response.headers['Content-Type'], 'application/json',
            error_msg.format('application/json', response.headers['Content-Type'], response.data))
        return json.loads(response.data.decode('utf-8'))

    def put_resource(self, url, data, expected_code = 200):
        error_msg = 'Expected {}, got {}. Data: {}'
        response = self.client.put(url, data = json.dumps(data),
                headers={'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'})
        self.assertEqual(response.status_code, expected_code,
            error_msg.format(expected_code, response.status_code, 'PUT to {} failed: {}'.format(url, response.data)))
        self.assertEqual(response.headers['Content-Type'], 'application/json',
            error_msg.format('application/json', response.headers['Content-Type'], response.data))
        return json.loads(response.data.decode('utf-8'))

    def delete_resource(self, url, expected_code = 200):
        error_msg = 'Expected {}, got {}. Data: {}'
        response = self.client.delete(url, headers={'X-Requested-With': 'XMLHttpRequest'})
        self.assertEqual(response.status_code, expected_code,
                         error_msg.format(expected_code,
                                          response.status_code,
                                          '\nWhile doing DELETE to {}.\nGot response:\n{}'.format(
                                              url,
                                              response.data)))
        self.assertEqual(response.headers['Content-Type'], 'application/json',
            error_msg.format('application/json', response.headers['Content-Type'], response.data))
        return json.loads(response.data.decode('utf-8'))
