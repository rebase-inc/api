from random import choice

def plural(text):
    known_forms = {
        'y': 'ies',
    }
    if text[-1] in known_forms.keys():
        return text[0:-1]+known_forms[text[-1]]
    else:
        return text+'s'

class AlveareResource(object):
    def __init__(self, test, resource):
        '''
        test is an AlveareTestCase
        resource is a string such as 'organization' or 'remote_work_history', matching the singular
        name of a resource
        '''
        self.test = test
        self.resource = resource
        self.col_url = plural(self.resource)
        self.url_format = (self.col_url+'/{}').format

    def url(self, resource):
        ''' returns the URL uniquely identifying 'resource'
        resource can be a dictionary (containing the primary keys) or an integer.
        If resource is an integer, the returned URL will be 'self.col_url+'/{resource}'
        if resource is a dictionary, the default implementation will assume the primary key is 'id'.
        You must therefore redefine this method for the dictionary case if your primary keys is not 'id' 
        or is composite.
        '''
        if isinstance(resource, int):
            return self.url_format(resource)
        else:
            return self.url_format(resource['id'])

    def get(self, resource_id):
        ''' helper function that returns the actual dictionary of fields for 'resource'/'resource_id'
        '''
        response = self.test.get_resource('{}/{}'.format(self.col_url, resource_id))
        self.test.assertIn(self.resource, response)
        return response[self.resource]

    def get_all(self):
        ''' returns all the instances of this resource
        '''
        response = self.test.get_resource(self.col_url)
        self.test.assertIn(self.col_url, response)
        all_resources = response[self.col_url]
        self.test.assertTrue(all_resources)
        return all_resources

    def get_any(self):
        ''' return any object from the collection of resources
        '''
        all_resources = self.get_all()
        any_res = choice(all_resources)
        res_response = self.test.get_resource(self.url(any_res))
        self.test.assertIn(self.resource, res_response)
        one_resource = res_response[self.resource]
        return one_resource

    def delete_any(self):
        resource_url = self.url(self.get_any())
        self.test.delete_resource(resource_url)
        self.test.get_resource(resource_url, 404)

    def compare(self, a, b):
        ''' verifies that each key, value in a is found in b '''
        for key, value in a.items():
            self.test.assertIn(key, b)
            self.test.assertEqual(b[key], value)

    def modify_or_create(self, rest_method, resource_url, **resource):
        response = rest_method(resource_url, resource)
        self.test.assertIn(self.resource, response)
        new_res = response[self.resource] 
        self.compare(resource, new_res)

        # verify the new resource has been committed to the database
        # by doing an independent request
        response = self.test.get_resource(self.url(new_res))
        self.test.assertIn(self.resource, response)
        queried_resource = response[self.resource]
        self.test.assertTrue(queried_resource)
        self.compare(resource, queried_resource)
        return queried_resource

    def create(self, **resource):
        return self.modify_or_create(self.test.post_resource, self.col_url, **resource)

    def update(self, **resource):
        return self.modify_or_create(self.test.put_resource, self.url(resource), **resource)

    def delete_related_resource(self, resource, related, related_id, persists):
        '''
        Delete 'related' and if persists is True, make sure resource is still available.
        If persists is False, make sure 'resource' has been deleted as well
        '''
        pass

