import json
import datetime
import unittest

from rebase import models, create_app
from rebase.common.mock import create_the_world, create_admin_user, create_one_user
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

        self.db.drop_all()
        self.db.create_all()
        self.db.session.commit()

        if self.create_mock_data:
            create_the_world(self.db)
            self.admin_user = create_admin_user(self.db, password='foo')
            self.db.session.commit()

        self.addCleanup(self.cleanup)

    def login_admin(self, role='manager'):
        self.login(self.admin_user.email, 'foo', role=role)

    def login(self, email, password, role=None):
        response = self.post_resource('/auth', { 'user': {'email': email}, 'password': password, 'role': role})
        user = response['user']
        current_role = user['current_role']
        #print('Logged in as {} with role "{}"'.format(user['email'], current_role))
        return user

    def logout(self):
        self.get_resource('/auth')

    def login_as_new_user(self):
        new_user = create_one_user(self.db)
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
        self.assertTrue(user)
        self.login(user.email, 'foo')
        return user

    def login_as_contractor_only(self, filters=None):
        ''' login as and return a non-admin user whose only role is contractor '''
        return self.login_as(['manager'], filters)

    def login_as_contractor_only_with_clearance(self, filters=None):
        ''' login as and return a non-admin user whose only role is contractor with some clearances '''
        def new_filters(query):
            new_query = query.join(Contractor).filter(Contractor.clearances.any())
            if filters:
                new_query = filters(new_query)
            return new_query

        return self.login_as(['manager'], new_filters)

    def login_as_manager_only(self, filters=None):
        '''
            Login as and return a non-admin user whose only role is manager.
            filters is same as with login_as method
        '''
        query = User.query\
            .join(User.roles)\
            .filter(Role.type.in_(['manager']))
        if filters:
            query = filters(query)
        user = query.first()
        self.assertTrue(user)
        self.login(user.email, 'foo')
        return user

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

    def _run(self, case, role):
        user, instance = case(self.db)
        self.login(user.email, 'foo', role)
        return user, instance

class MethodNotImplemented(NotImplementedError):
    error_msg = '{} does not implement PermissionTestCase.{}'
    def __init__(self, instance, method_name):
        super().__init__(self.error_msg.format(self.__class__.__name__, method_name))

class PermissionTestCase(RebaseNoMockRestTestCase):
    '''
    TestCase don't use __init__ constructor, so we use static member 'model' to describe
    which model the resource is describing
    Classe deriving from PermissionTestCase must:
    - overwrite 'model' to define it. For example model='TicketSet'
    - define an implementation for these methods:
        - new
        - validate_view
    '''

    create_mock_data = False
    model = None

    def setUp(self):
        if not self.model:
            raise TypeError('Classes deriving from PermissionTestCase must set their "model" member to a valid class from rebase.models')
        self.resource = RebaseResource(self, self.model)
        super().setUp()

    def collection(self, case, role):
        user, thing = self._run(case, role)
        if isinstance(thing, list):
            expected_resources = thing
        elif not thing:
            expected_resources = []
        else:
            expected_resources = [thing]
        validate_resource_collection(self, expected_resources)

    def validate_view(self, instance):
        '''
        Validate the dict returned by a GET to the API
        '''
        raise MethodNotImplemented(self, 'validate_view')

    def view(self, case, role, allowed_to_view):
        _, instance = self._run(case, role)
        instance_blob = self.resource.get(ids(instance), 200 if allowed_to_view else 401)
        if allowed_to_view:
            self.validate_view(instance_blob)
        return instance_blob

    def update(self, instance):
        '''
        Given a SQLAlchemy model instance, return its equivalent dict with potentially modified fields
        '''
        raise MethodNotImplemented(self, 'update')

    def validate_modify(_, test_resource, requested, returned):
        '''
        Classes deriving from this class should provide their own implementation.
        The default implementation performs RebaseResource.validate_response
        '''
        test_resource.validate_response(requested, returned)

    def modify(self, case, role, allowed_to_modify):
        _, instance = self._run(case, role)
        modified_blob = self.update(instance)
        self.resource.update(expected_status=200 if allowed_to_modify else 401, validate=self.validate_modify,  **modified_blob)

    def delete(self, case, role,  allowed_to_delete):
        _, instance = self._run(case, role)
        instance_blob = ids(instance)
        self.resource.delete(expected_status=200 if allowed_to_delete else 401, **instance_blob)

    def new(self, old_instance):
        '''Given instance, will return a dict for a new instance of the same resource type.'''
        raise MethodNotImplemented(self, 'new')

    def create(self, case, role, allowed_to_create, validate=None, delete_first=False):
        '''
        *case* is a function with no param that return a tuple (logged_in_user, instance)
        where logged_in_user is the user that is assumed to be logged in and instance is some instance of resource type.

        *role* is the role the user logging in as

        *allowed_to_create* is a boolean, True means logged_in_user can create another instance, False means it's forbidden (resource will return 401).


        *validate* is a function (new_blob, response) which tests the response of the POST against the new_blob submitted in the request.
        If left to None, a default validate is performed by the RebaseResource object associated with the model.

        *delete_first* if True will delete the instance returned by the last call to the case function.
        This is useful when a DB model has a unique constraint on one of many of its fields

        '''
        user, instance = self._run(case, role)
        new_instance_blob = self.new(instance)
        if delete_first:
            self.db.session.delete(instance)
            self.db.session.commit()
        self.resource.create(expected_status=201 if allowed_to_create else 401, validate=validate, **new_instance_blob)

