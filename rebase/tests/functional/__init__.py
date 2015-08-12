import json
import datetime
import unittest

from rebase import models, create_app
from rebase.common.mock import create_the_world, create_admin_user
from rebase.models import (
    User,
    CodeClearance,
    Contractor,
    Role,
)

class RebaseRestTestCase(unittest.TestCase):
    create_mock_data = True

    def setUp(self):
        self.app, self.app_context, self.db = create_app(testing=True)

        self.client = self.app.test_client()

        self.db.create_all()
        self.db.session.commit()

        if self.create_mock_data:
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
        self.login(new_user.email, 'foo')

    def login_as(self, exclude_roles=None, filters=None):
        '''
            Login as and return a non-admin user whose only roles are not listed in exclude_roles

            filters, optional, will be applied to the basic query
            to further reduce the query results.

            filters function must have the following signature:
            def filters(query)
                return new_query # new_query is any query
        '''
        query = User.query\
            .join(User.roles)\
            .filter(~User.roles.any(Role.type.in_(exclude_roles or [])))\
            .filter(~User.admin)
        if filters:
            query = filters(query)
        user = query.first()
        self.login(user.email, 'foo')
        return user

    def login_as_contractor_only(self, filters=None):
        ''' login as and return a non-admin user whose only role is contractor '''
        return self.login_as(['manager'], filters)

    def login_as_contractor_only_with_clearance(self, filters=None):
        ''' login as and return a non-admin user whose only role is contractor with some clearances '''
        def new_filters(query):
            new_query = query.join(Contractor).join(CodeClearance)
            if filters:
                new_query = filters(new_query)
            return new_query

        return self.login_as(['manager'], new_filters)

    def login_as_manager_only(self, filters=None):
        '''
            Login as and return a non-admin user whose only role is manager.
            filters is same as with login_as method
        '''
        return self.login_as(['contractor'], filters)

    def login_as_no_role_user(self):
        ''' login as return non-admin user with role '''
        #return self.login_as(['contractor', 'manager'])
        user = User.query\
            .filter(~User.roles.any())\
            .filter(~User.admin)\
            .first()
        self.login(user.email, 'foo')
        return user

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
        error_msg_fmt = 'Expected {}, got {}. Data: {}'
        # the header is required because of flask jsonify
        # see http://stackoverflow.com/questions/16908943/flask-display-json-in-a-neat-way
        response = self.client.get(url, headers={'X-Requested-With': 'XMLHttpRequest'})
        error_msg = error_msg_fmt.format(
            expected_code,
            response.status_code,
            'GET to {} failed: {}'.format(url, response.data))
        self.assertEqual(response.status_code, expected_code, error_msg)
        error_msg = error_msg_fmt.format('application/json', response.headers['Content-Type'], response.data)
        self.assertEqual(response.headers['Content-Type'], 'application/json', error_msg)
        return json.loads(response.data.decode('utf-8'))

    def post_resource(self, url, data=dict(), expected_code = 201):
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
        self.assertEqual(
            response.status_code,
            expected_code,
            error_msg.format(
                expected_code,
                response.status_code,
                '\n while doing PUT to {}.\nGot response:\n{}'.format(url, response.data)
            )
        )
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

class RebaseNoMockRestTestCase(RebaseRestTestCase):
    create_mock_data = False

    def setUp(self):
        super().setUp()
