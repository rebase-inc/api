from sqlalchemy.inspection import inspect

def get_model_primary_keys(model):
    ''' returns the tuple of names of components of the primary key
    e.g get_model_primary_keys(Foo<('id1', 'id2')>)  => ('id1', 'id2')
    '''
    return tuple(map(lambda key: key.name, inspect(model).primary_key))

def make_collection_url(model):
    return '/'+ model.__pluralname__

def make_resource_url(model):
    keyspace_format = ''
    for primary_key in get_model_primary_keys(model):
        keyspace_format += '/<int:{}>'.format(primary_key)
    return make_collection_url(model) + keyspace_format

def primary_key(instance):
    ''' given an instance, returns the value of the primary key
    e.g Foo<('id1':1, 'id2':5)>  => (1, 5)
    '''
    return inspect(instance).identity

def ids(instance):
    ''' return a dictionary of with the ids of instance
    e.g. ids(some_db_class) => {'a': 1, 'b':3} where (a, b) is the primary key of some_db_class
    '''
    return dict(zip(get_model_primary_keys(type(instance)), primary_key(instance)))

