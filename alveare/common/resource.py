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

def primary_key(model):
    return list(map(lambda key: key.name, inspect(model).primary_key))

def get_or_make_object(model, data, ids=['id']):
    if ids[0] in data:
        id = tuple( data[key] for key in ids )
        instance = model.query.get(id)
        if not instance:
            data['__name'] = model.__tablename__
            raise ValueError('No {__name} with id {id}'.format(id=id, **data))
        return instance
    return model(**data)

def update_object(model, data, ids=['id']):
    if ids[0] in data:
        instance = get_or_make_object(model, data, ids)
        for key, value in data.items():
            if key in ids: continue
            if getattr(instance, key) != value:
                setattr(instance, key, value)
        return instance
    else:
        data['__name'] = model.__tablename__
        raise ValueError('No {__name} id given!'.format(**data))

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
        self.col_url = plural(self.resource)
        url_format = ''
        self.primary_key = primary_key(model)
        for key in self.primary_key:
            url_format += '/{}'
        self.url_format = (self.col_url+url_format).format

    def url(self, resource):
        ''' returns the URL uniquely identifying 'resource'
        resource can be a dictionary (containing the primary keys) or an integer.
        If resource is an integer, the returned URL will be 'self.col_url+'/{resource}'
        '''
        if isinstance(resource, int):
            return self.url_format(resource)
        return self.url_format(*(map(lambda key: resource[key], self.primary_key)))

    def get(self, resource, expected_status=200):
        ''' helper function that returns the actual dictionary of fields for 'resource'/'resource_id'
        '''
        response = self.test.get_resource(self.url(resource), expected_status)
        if expected_status == 404:
            return None
        self.test.assertIn(self.resource, response)
        return response[self.resource]

    def delete(self, resource):
        self.test.delete_resource(self.url(resource))
        self.test.get_resource(self.url(resource), 404)

    def get_all(self):
        ''' returns all the instances of this resource
        '''
        response = self.test.get_resource(self.col_url)
        self.test.assertIn(self.col_url, response)
        all_resources = response[self.col_url]
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

    def dict_in(self, a, b):
        for key, value in a.items():
            self.test.assertIn(key, b)
            self.is_in(value, b[key])

    type_to_compare = {
        type(dict()):   dict_in,
        #type(list):    list_in, # TODO implement if need be
        #type(set):     set_in
    }

    def is_in(self, a, b):
        '''
            Verify that a is found in b, if a and b are composites.
            If they are scalars, verify that they are equal.
        '''
        if type(a) != type(b):
            raise ValueError('Trying to compare {} to {}'.format(type(a), type(b)))
        if type(a) in AlveareResource.type_to_compare.keys():
            try:
                AlveareResource.type_to_compare[type(a)](self, a, b)
            except AssertionError as e:
                raise ValueError('Caught exception {}\nwhile comparing:\n {}\nto\n{}'.format(e, a, b))
        else:
            self.test.assertEqual(a, b)

    def modify_or_create(self, rest_method, resource_url, **resource):
        response = rest_method(resource_url, resource)
        self.test.assertIn(self.resource, response)
        new_res = response[self.resource]
        self.is_in(resource, new_res)

        # verify the new resource has been committed to the database
        # by doing an independent request
        response = self.test.get_resource(self.url(new_res))
        self.test.assertIn(self.resource, response)
        queried_resource = response[self.resource]
        self.test.assertTrue(queried_resource)
        self.is_in(resource, queried_resource)
        return queried_resource

    def create(self, **resource):
        return self.modify_or_create(self.test.post_resource, self.col_url, **resource)

    def update(self, **resource):
        return self.modify_or_create(self.test.put_resource, self.url(resource), **resource)
