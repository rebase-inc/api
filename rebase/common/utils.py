from random import choice, seed
from collections import defaultdict
from inspect import getmembers, isclass
from platform import system
from keyword import kwlist

from sqlalchemy.inspection import inspect

import rebase.models

def plural(text):
    known_forms = {
        'y': 'ies',
        'h': 'hes',
    }
    if text[-1] in known_forms.keys():
        return text[0:-1]+known_forms[text[-1]]
    else:
        return text+'s'

def get_model_primary_keys(model):
    return tuple(map(lambda key: key.name, inspect(model).primary_key))

def primary_key(instance):
    return inspect(instance).identity

def make_collection_url(model):
    return '/'+ model.__pluralname__

def make_resource_url(model):
    keyspace_format = ''
    for primary_key in get_model_primary_keys(model):
        keyspace_format += '/<int:{}>'.format(primary_key)
    return make_collection_url(model) + keyspace_format

def resource_url(model, use_flask_format=False):
    '''
        Given a model, return the URL format string for a single resource
        if use_flask_format is True, return the URL format for Flask routes

        NOTE: This makes a huge assumption that the names of the parameters
        returned are the exact same as the names of the fields on the db model.
        So, this will not work if you ever use the attribute parameter on a
        marshmallow schema for a particular object
    '''
    url_format = ''
    for key in get_model_primary_keys(model):
        if use_flask_format:
            url_format += '/<int:'+key+'>'
        else:
            url_format += '/{}'
    return make_collection_url(model)+url_format

composite_error_not_in='''
While comparing first:
{}
to second:
{}
Key "{}" was not found in second'''

composite_error_not_equal='''
'While comparing first:
{}
to second:
{}
first[{key}] != second[{key}]
{e}'''

class RebaseResource(object):

    all_models = dict(getmembers(rebase.models, predicate=isclass))

    def __init__(self, test, resource):
        '''
        test is an RebaseTestCase
        resource is a string such as 'Organization' or 'RemoteWorkHistory', matching the name of a model
        '''
        if resource not in self.all_models:
            raise ValueError('Unknown model "{}"'.format(resource))
        model = self.all_models[resource]
        self.test = test
        self.resource = model.__tablename__

        self.collection_url = plural(self.resource)
        self.primary_key = get_model_primary_keys(model)
        self.url_format = resource_url(model).format

    def url(self, resource):
        ''' returns the URL uniquely identifying 'resource'
        resource can be a dictionary (containing the primary keys) or an integer.
        If resource is an integer, the returned URL will be 'self.collection_url+'/{resource}'
        '''
        if isinstance(resource, int):
            return self.url_format(resource)
        try:
            return self.url_format(*(map(lambda key: resource[key], self.primary_key)))
        except KeyError as e:
            raise ValueError('Cant format {} with {}'.format(resource_url(model), resource))

    def just_ids(self, resource):
        '''
            Given a resource dict, return its sub-dict containing only its keys
            For instance:
            just_ids({
                'contractor_id':    1,
                'name':             'Joe'
                })

            returns {'contractor_id: 1}
        '''
        return dict( (key, resource[key]) for key in self.primary_key )

    def get(self, resource, expected_status=200):
        ''' helper function that returns the actual dictionary of fields for 'resource'/'resource_id'
        '''
        response = self.test.get_resource(self.url(resource), expected_status)
        if expected_status in [401, 404]:
            return None
        self.test.assertIn(self.resource, response)
        return response[self.resource]

    def delete(self, validate=True, expected_status=200, **resource):
        
        self.test.delete_resource(self.url(resource), expected_status)
        if expected_status in [401, 404]:
            return None
        if validate:
            self.test.get_resource(self.url(resource), 404)

    def get_all(self, expected_status_code=200):
        ''' returns all the instances of this resource
        '''
        response = self.test.get_resource(self.collection_url, expected_code=expected_status_code)
        if expected_status_code in [401, 404]:
            return None
        self.test.assertIn(self.collection_url, response)
        return response[self.collection_url]

    def get_any(self, seed_value=None):
        '''
            Return any object from the collection of resources.
            seed_value will optionally be used to initialize the random generator.
            If you need a deterministic behavior (while debugging for instance), always provide the same value.
        '''
        all_resources = self.get_all()
        if not all_resources:
            return None
        if seed_value:
            seed(seed_value)
        any_res = choice(all_resources)
        res_response = self.test.get_resource(self.url(any_res))
        self.test.assertIn(self.resource, res_response)
        one_resource = res_response[self.resource]
        return one_resource

    def delete_any(self, seed_value=None):
        ''' deletes any object from this resource and returns the deleted object '''
        resource = self.get_any(seed_value)
        self.test.assertTrue(resource)
        resource_url = self.url(resource)
        self.test.delete_resource(resource_url)
        self.test.get_resource(resource_url, 404)
        return resource

    def assertComposite(self, first, second, recurse=False):
        '''
            Verify that first is found in second, if first and second are composites.
            If they are scalars, verify that they are equal.
        '''
        if type(first) != type(second):
            raise ValueError('Trying to compare {} to {}'.format(type(first), type(second)))
        if isinstance(first, dict):
                for key, value in first.items():
                    try:
                        if recurse:
                            self.assertComposite(value, second[key])
                        else:
                            self.test.assertEqual(value, second[key])
                    except KeyError as e:
                        raise AssertionError(composite_error_not_in.format(
                            first,
                            second,
                            key
                        ))
                    except AssertionError as e:
                        raise AssertionError(composite_error_not_equal.format(
                            first,
                            second,
                            key=key,
                            e=e
                        ))
        else:
            self.test.assertEqual(first, second)

    def validate_response(self, resource, response):
        '''
        Performs a number of assertions on the response and returns the new resource
        '''
        self.test.assertIn(self.resource, response)
        new_res = response[self.resource]
        self.assertComposite(resource, new_res)

        # verify the new resource has been committed to the database
        # by doing an independent request
        response = self.test.get_resource(self.url(new_res))
        self.test.assertIn(self.resource, response)
        queried_resource = response[self.resource]
        self.test.assertTrue(queried_resource)
        self.assertComposite(resource, queried_resource)
        return queried_resource

    def modify_or_create(
        self,
        rest_method,
        resource_url,
        validate=validate_response,
        expected_status=200,
        **resource
    ):
        '''
        Executes the rest method and validates the response if desired.
        validate must be a method bound to self with the same signature as validate_response
        If validate is None, no validation is performed and the new resource is returned directly
        '''
        response = rest_method(resource_url, resource, expected_status)
        if expected_status in [401, 404]:
            return None
        if validate:
            return validate(self, resource, response)
        return response[self.resource]

    def create(self, validate=validate_response, expected_status=201, **resource):
        return self.modify_or_create(
            self.test.post_resource,
            self.collection_url,
            validate=validate,
            expected_status=expected_status,
            **resource
        )

    def update(self, validate=validate_response, expected_status=200, **resource):
        return self.modify_or_create(
            self.test.put_resource,
            self.url(resource),
            validate=validate,
            expected_status=expected_status,
            **resource
        )

def validate_query_fn(test, klass, case, query_fn, create, modify, delete, view):
    user, resource = case(test.db)
    expected_resources = [resource] if resource else []
    another_user, one_more_resource = case(test.db) # create more unrelated resource, to make sure the queries discriminate properly
    if user.admin:
        expected_resources.append(one_more_resource)
    resources = query_fn(user).all()
    test.assertEqual(expected_resources, resources)
    test.assertEqual(expected_resources, klass.query_by_user(user).all())
    if resource:
        test.assertEqual(create, bool(resource.allowed_to_be_created_by(user)))
        test.assertEqual(modify, bool(resource.allowed_to_be_modified_by(user)))
        test.assertEqual(delete, bool(resource.allowed_to_be_deleted_by(user)))
        test.assertEqual(view,   bool(resource.allowed_to_be_viewed_by(user)))

def validate_resource_collection(test, logged_in_user, expected_resources):
    test.login(logged_in_user.email, 'foo')
    resources = test.resource.get_all() # test GET collection
    test.assertEqual(len(resources), len(expected_resources))
    resources_ids = [res['id'] for res in resources]
    for _res in expected_resources:
        test.assertIn(_res.id, resources_ids)
        one_res = test.resource.get(_res.id) # test GET one resource
        test.assertTrue(one_res)

dictionaries = defaultdict(list, {
    '/usr/share/dict/words':        [],
    '/usr/share/dict/propernames':  [],
})

if system() == 'Linux':
    dictionaries['/usr/share/dict/words'] = kwlist
    dictionaries['/usr/share/dict/propernames'] = [
        'Joe', 'Mikey', 'Raif', 'Randell', 'Albert', 'Jones', 'Dominick', 'Walt',
        'Jim', 'Morgan', 'Sedovic', 'Kieran', 'Panzer', 'Damon', 'Tuan', 'Win',
        'Cindie', 'Max', 'Barry', 'Sumitro', 'Leonard',
    ]
elif system() == 'Darwin':
    for dictionary in dictionaries.keys():
        max_num_items = 2000
        words = []
        for word in open(dictionary):
            words.append(word.rstrip())
        if len(words) > max_num_items:
            this_dictionary = dictionaries[dictionary]
            for i in range(max_num_items):
                this_dictionary.append(choice(words))
        else:
            dictionaries[dictionary] = words


def pick_a_word(min_size=0, max_size=100, dictionary='/usr/share/dict/words'):
    # build a one-time cache, limit size of each dictionary to max_num_items
            
    if min_size > 0 or max_size != 100:
        return choice(list(filter(lambda word: (min_size <= len(word)) and (len(word)<= max_size), dictionaries[dictionary])))
    return choice(dictionaries[dictionary])

def pick_a_first_name(min_size=0, max_size=100, dictionary='/usr/share/dict/propernames'):
    return pick_a_word(min_size, max_size, dictionary)

def pick_a_last_name(min_size=0, max_size=100):
    return pick_a_first_name(min_size, max_size)[::-1].capitalize()

def pick_an_organization_name(min_size=0, max_size=100):
    return pick_a_word(min_size, max_size).capitalize()+' '+choice(['Inc.', 'LLC', 'Foundation', 'Corporation'])
