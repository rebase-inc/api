from random import choice, seed
import alveare.models
from inspect import getmembers, isclass
from sqlalchemy.inspection import inspect


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

class AlveareResource(object):

    all_models = dict(getmembers(alveare.models, predicate=isclass))

    def __init__(self, test, resource):
        '''
        test is an AlveareTestCase
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

    def delete(self, expected_status=200, **resource):
        self.test.delete_resource(self.url(resource), expected_status)
        if expected_status in [401, 404]:
            return None
        self.test.get_resource(self.url(resource), 404)

    def get_all(self, expected_status_code=200):
        ''' returns all the instances of this resource
        '''
        response = self.test.get_resource(self.collection_url, expected_code=expected_status_code)
        if expected_status_code in [401, 404]:
            return None
        self.test.assertIn(self.collection_url, response)
        all_resources = response[self.collection_url]
        self.test.assertTrue(all_resources)
        return all_resources

    def get_any(self, seed_value=None):
        '''
            Return any object from the collection of resources.
            seed_value will optionally be used to initialize the random generator.
            If you need a deterministic behavior (while debugging for instance), always provide the same value.
        '''
        all_resources = self.get_all()
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
        resource_url = self.url(resource)
        self.test.delete_resource(resource_url)
        self.test.get_resource(resource_url, 404)
        return resource

    def assertComposite(self, first, second):
        '''
            Verify that first is found in second, if first and second are composites.
            If they are scalars, verify that they are equal.
        '''
        if type(first) != type(second):
            raise ValueError('Trying to compare {} to {}'.format(type(first), type(second)))
        if isinstance(first, dict):
                for key, value in first.items():
                    try:
                        self.assertComposite(value, second[key])
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

    def modify_or_create(self, rest_method, resource_url, expected_status=200, **resource):
        response = rest_method(resource_url, resource, expected_status)
        if expected_status in [401, 404]:
            return None
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

    def create(self, expected_status=201, **resource):
        return self.modify_or_create(self.test.post_resource, self.collection_url, expected_status, **resource)

    def update(self, expected_status=200, **resource):
        return self.modify_or_create(self.test.put_resource, self.url(resource), expected_status, **resource)
