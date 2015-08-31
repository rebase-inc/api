import json
import datetime
import unittest

from rebase import models, create_app
from rebase.common.mock import create_the_world, create_admin_user
from rebase.common.utils import RebaseResource, validate_resource_collection, ids
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
            self.admin_user = create_admin_user(self.db, password='foo')
            self.db.session.commit()

        self.addCleanup(self.cleanup)

    def login_admin(self):
        self.post_resource('/auth', { 'user': {'email': self.admin_user.email}, 'password': 'foo'})

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

class PermissionTestCase(RebaseNoMockRestTestCase):
    '''
    TestCase don't use __init__ constructor, so we use static member 'model' to describe
    which model the resource is describing
    Each class deriving from PermissionTestCase will overwrite 'model' to define it.
    '''

    create_mock_data = False
    model = None

    def setUp(self):
        if not self.model:
            raise TypeError('Classes deriving from PermissionTestCase must set their "model" member to a valid class from rebase.models')
        self.resource = RebaseResource(self, self.model)
        super().setUp()

    def _run(self, case):
        user, instance = case(self.db)
        self.login(user.email, 'foo')
        return user, instance

    def _collection(self, case):
        user, instance = self._run(case)
        validate_resource_collection(self, user, [instance] if instance else [])

    def _view(self, case, view, validate=None):
        _, instance = self._run(case)
        instance_blob = self.resource.get(ids(instance), 200 if view else 401)
        if view and validate:
            validate(self, instance_blob)
        return instance_blob

    def _modify(self, case, allowed_to_modify, modify_this=None):
        _, instance = self._run(case)
        if modify_this:
            modified_blob = modify_this(instance)
        else:
            modified_blob = ids(instance)
        self.resource.update(expected_status=200 if allowed_to_modify else 401, **modified_blob)

    def _delete(self, case,  delete):
        _, instance = self._run(case)
        instance_blob = ids(instance)
        self.resource.delete(expected_status=200 if delete else 401, **instance_blob)

    def _create(self, case, create, new_instance, validate=None, delete_first=False):
        '''
        *case* is a function with no param that return a tuple (logged_in_user, instance)
        where logged_in_user is the user that is assumed to be logged in and instance is some instance of resource type.

        *create* is a boolean, True means logged_in_user can create another instance, False means it's forbidden (resource will return 401).

        *new_instance* is a function that given instance, will return a dict for a new instance of the same resource type.

        *validate* is a function (new_blob, response) which tests the response of the POST against the new_blob submitted in the request.
        If left to None, a default validate is performed by the RebaseResource object associated with the model.

        *delete_first* if True will delete the instance returned by the last call to the case function.
        This is useful when a DB model has a unique constraint on one of many of its fields

        '''
        user, instance = self._run(case)
        new_instance_blob = new_instance(instance)
        if delete_first:
            delete_blob = ids(instance)
            self.resource.delete(expected_status=200, **delete_blob)
        self.resource.create(expected_status=201 if create else 401, validate=validate, **new_instance_blob)

