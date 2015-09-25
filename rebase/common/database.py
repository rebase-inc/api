from functools import lru_cache, partialmethod

from sqlalchemy.inspection import inspect
from sqlalchemy.orm.collections import InstrumentedList

from marshmallow import fields
from flask.ext.login import current_user
from flask.ext.sqlalchemy import SQLAlchemy
from rebase.common.exceptions import (
    BadDataError,
    NotFoundError,
    AsContractorPathUndefined,
    AsManagerPathUndefined,
)
from rebase.common.query import query_from_class_to_user


DB = SQLAlchemy()
DB_PRODUCTION_NAME = 'rebase'
DB_TEST_NAME = 'test_'+DB_PRODUCTION_NAME

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

def get_or_make_object(model, data, id_fields=None):
    id_fields = get_model_primary_keys(model)
    instance_id = tuple(data.get(id_field) for id_field in id_fields)
    if all(instance_id):
        instance = model.query.get(instance_id)
        if not instance:
            raise NotFoundError(model.__tablename__, instance_id)
        return instance
    elif not data:
        raise BadDataError(model_name=model.__tablename__)
    return model(**data)


# TODO implement incremental hashing
def _setitem(ilist, index, element):
    current_hash = getattr(ilist, '__current_hash__', 0)

def _hash(ilist):
    pile = ''
    for elt in ilist:
        pile = pile+str(elt)
    return hash(pile)

setattr(InstrumentedList, '__hash__', _hash)

class SecureNestedField(fields.Nested):
    def __init__(self, nested, strict=False, *args, **kwargs):
        self.strict = strict
        super().__init__(nested, *args, **kwargs)

    @lru_cache(maxsize=None)
    def _serialize_with_user(self, nested_obj, attr, obj, user):
        if not nested_obj:
            if self.many:
                return []
            else:
                return None
        if not user:
            raise ValueError('Current user not supplied to {} nested on {}'.format(nested_obj, obj))
        if self.many:
            nested_obj = [elem for elem in nested_obj if elem.allowed_to_be_viewed_by(user)]
        else:
            nested_obj = nested_obj if nested_obj.allowed_to_be_viewed_by(user) else None
        self.schema.context = self.context
        return super()._serialize(nested_obj, attr, obj)

    _serialize = partialmethod(_serialize_with_user, user=current_user)

    @property
    def schema(self):
        _schema = fields.Nested.schema.fget(self)
        _schema.strict = self.strict
        return _schema


class PermissionMixin(object):
    as_contractor_path = None
    as_manager_path = None

    def allowed_to_be_created_by(self, user):
        msg = 'allowed_to_be_created_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_modified_by(self, user):
        msg = 'allowed_to_be_modified_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_deleted_by(self, user):
        msg = 'allowed_to_be_deleted_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    def allowed_to_be_viewed_by(self, user):
        msg = 'allowed_to_be_viewed_by not implemented for {}'
        raise NotImplementedError(msg.format(type(self).__name__))

    @classmethod
    def query_from_class_to_user(klass, path, user):
        query = klass.query
        for node in path:
            query = query.join(node)
        query = query.filter((path[-1].user if path else klass.user) == user)
        return query

    @classmethod
    def as_contractor(cls, user):
        if cls.as_contractor_path == None:
            raise AsContractorPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_contractor_path, user)

    @classmethod
    def as_manager(cls, user):
        if cls.as_manager_path == None:
            raise AsManagerPathUndefined(cls)
        return cls.query_from_class_to_user(cls.as_manager_path, user)

    @classmethod
    def role_to_query_fn(cls, user):
        if user.current_role.type == 'manager':
            return cls.as_manager
        elif user.current_role.type == 'contractor':
            return cls.as_contractor
        else:
            raise UnknownRole(user.current_role)

    @classmethod
    def query_by_user(cls, user):
        if user.is_admin():
            return cls.query
        return cls.role_to_query_fn(user)(user)

    @classmethod
    def setup_queries(cls, _):
        msg = 'setup_queries is not implemented for {}'
        #raise NotImplemented(msg.format(cls.__name__))
        #print(msg.format(cls.__name__))


def query_by_user_or_id(cls, query_fn, filter_by_id, user, instance=None):
    if user.admin:
        query = cls.query
    else:
        query = query_fn(user)
    if instance:
        query = instance.filter_by_id(query)
    return query
